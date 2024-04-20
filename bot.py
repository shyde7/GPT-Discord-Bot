# youre gonna have to install the following packages to run the bot
# pip install discord
# pip install discord.py
# pip install openai
# pip install psycopg2
# pip install asyncio
# pip install flask

import discord
from discord.ext import commands
from flask_server import keep_alive
import os
import openai
import psycopg2
import asyncio

conn_params = {
    'dbname': 'EQ Items',
    'user': 'postgres',
    'password': 'password',
    'host': 'localhost'
}

CHANNEL_ID = 1228003840348000319

DISCORD_BOT_TOKEN = 'MTIyODAwMzc2OTM1OTQwMTEwMw.GrK4QD.6lPErP9_nnDJlStf1Q13g5xNaxeL-hxl-PstXY'
OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define the intents we want to use
intents = discord.Intents.all()
intents.messages = True
intents.guilds = True

# Initialize the OpenAI API client
openai.api_key = OPEN_AI_API_KEY



class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="GPT Powered EverQuest Item Finder",
            description="Hello! I take natural language questions about EverQuest items and convert them to SQL queries to find the items you're looking for. Here's how you can use me:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands",
            value=(
                "`!finditem <question>`: Ask a question about an EverQuest item or spell and I'll find it for you.\n\n"
            ),
            inline=False
        )
        embed.add_field(
            name="Examples",
            value=(
                "`!finditem find me a sword` \n\n"
            ),
            inline=False
        )
        embed.set_footer(text="Powered by OpenAI's GPT-3.5 API and PostgreSQL database.")

        channel = self.get_destination()
        await channel.send(embed=embed)

# Initialize the bot with the desired command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents, help_command=CustomHelpCommand())

@bot.event 
async def on_ready():
    print("Bot is ready")
    channel = bot.get_channel(CHANNEL_ID) 
    embed = discord.Embed(
        title="Hello, I'm your EverQuest Item Finder Bot!",
        description="I can help you find EverQuest items using natural language queries. Ask me anything about EverQuest items and I'll do my best to find them for you.",
        color=discord.Color.blurple()
    )

    await channel.send(embed=embed)

@bot.command()
async def finditem(ctx, *, question: str):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an EverQuest professional, able to query a large database with items and spells. Convert questions into SQL queries." 
                "Expected output format: 'SELECT * FROM items WHERE name LIKE '%Sword%';'"
                "The columns you can query from are:name, lore, idfile, idfileextra, id, weight, size, attunable, slots, price, mana, regen, manaregen, classes, races, deity, reclevel, reqskill, damage"},
                "Here are how the "
                {"role": "user", "content": question}
            ],
            max_tokens=100,
            temperature=0.5
        )

        sql_query = response['choices'][0]['message']['content'].strip()
        print("Here is the question:", question)
        print("Attempting to execute SQL query:", sql_query)

        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute(sql_query)
        results = cur.fetchall()
        conn.close()

        page = 0
        page_size = 10  # Set the number of items per page

        def create_embed(page):
            start = page * page_size
            end = start + page_size
            embed = discord.Embed(
                title="Search Results",
                description="Here are the items that match your search:",
                color=discord.Color.green()
            )
            for result in results[start:end]:
                embed.add_field(
                    name=result[1],  # Assuming the name is in the second column
                        value="Price: " + str(result[10]) + ", ID: " + str(result[5]),  # Ensure all numeric values are converted to strings
                    inline=False
                )
            embed.set_footer(text=f"Page {page+1} of {len(results) // page_size + (1 if len(results) % page_size > 0 else 0)}")
            return embed

        message = await ctx.send(embed=create_embed(page))
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                if str(reaction.emoji) == "▶️" and page < len(results) // page_size:
                    page += 1
                    await message.edit(embed=create_embed(page))
                    await message.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "◀️" and page > 0:
                    page -= 1
                    await message.edit(embed=create_embed(page))
                    await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")
        
keep_alive()
bot.run(DISCORD_BOT_TOKEN)
