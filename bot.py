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

#replace with whatever your channel id is 
#enable discord dev mode and copy and paste it.
CHANNEL_ID = 1232498730817552506

preferred_channel_id = None

DISCORD_BOT_TOKEN = 'MTIyODAwMzc2OTM1OTQwMTEwMw.GrK4QD.6lPErP9_nnDJlStf1Q13g5xNaxeL-hxl-PstXY'
OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define the intents we want to use
intents = discord.Intents.all()
intents.messages = True
intents.guilds = True

# Initialize the OpenAI API client
openai.api_key = OPEN_AI_API_KEY


class CustomHelpCommand(commands.HelpCommand):
    def get_command_signature(self, command):
        return f'`!{command.qualified_name} {command.signature}`'

    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="GPT Powered EverQuest Item Finder Help",
            description="I can help you find items and details from the EverQuest universe. Below are the commands you can use:",
            color=discord.Color.blue()
        )
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "Commands")
                embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        embed.add_field(
            name="Examples",
            value=(
                "`!finditem find me a sword` - Searches for a sword.\n"
                "`!itemdetails 123` - Shows details for the item with ID 123.\n"
                # Add more examples if needed
            ),
            inline=False
        )
        embed.set_footer(text="Powered by OpenAI's GPT-3.5 API and PostgreSQL database.")

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f'Help with `{command.name}` command',
            description=command.help or "No description available",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="Usage",
            value=self.get_command_signature(command),
            inline=False
        )
        await self.get_destination().send(embed=embed)

# Initialize the bot with the desired command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents, help_command=CustomHelpCommand())
bot.help_command = CustomHelpCommand()

@bot.event 
async def on_ready():
    print("Bot is ready")
    channel = bot.get_channel(CHANNEL_ID) 
    embed = discord.Embed(
        title="Hello, I'm your EverQuest Item Finder Bot!",
        description="I'm here to help you find EQ items and spells!",
        color=discord.Color.blurple()
    )
    embed.add_field(
        name = "What I Do",
        value = "I take natural language questions about EverQuest items and convert them to SQL queries to find the items you're looking for.",
        inline = False
    )
    embed.add_field(
        name = "How to Use Me",
        value = "Just type `!finditem <question>` to get started!\n Try `!itemdetails <item_id>` to get details about a specific item.",
        inline = False
    )
    embed.add_field(
        name = "Help Command",
        value = "Use `!help` if you forget how to use me!",
        inline = False
    )

    embed.set_footer(text="Powered by OpenAI's GPT-3.5 API and PostgreSQL database.")


    await channel.send(embed=embed)

@bot.command()
async def finditem(ctx, *, question: str):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an EverQuest professional, able to query a large database with items and spells. Convert questions into SQL queries." 
                "Expected output format: 'SELECT * FROM items WHERE name LIKE '%Sword%';'"
                "The columns you can query from are: name, lore, idfile, idfileextra, id, weight, size, attunable, price, mana, regen, manaregen, classes, races, deity, reclevel, reqskill, damage."
                "Priortize using the name column for the best results."},
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
        name=f"**{result[1]}**",  # Item name in bold
        value=(f"\n**Price:** {result[8]}, "
               f"**ID:** {result[5]}, "
               f"**HP:** {result[9]}, "
               f"**Mana:** {result[10]}, "
               f"**Recommended Level:** {result[18]}, "
               f"**Required Skill:** {result[19]}"),  # Attributes in bold
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
        # Handle errors and send a embed message to the user
        embed = discord.Embed(
            title="Error Occurred in Processing Request 😔",
            description=f"An error occurred while processing your request: {str(e)}",
            color=discord.Color.red()
        )
        embed.add_field(
            name = "Please Try Again",
            value = "Make sure your question is clear and concise.",
            inline = False
        )
        embed.add_field(
            name = "Best Practices",
            value = "Try structuring your question like a Database query for best results. \n\nFor example, 'Find me a sword with a price less than 1000 platinum.'",
            inline = False
        )
        print(f"An error occurred: {str(e)}")

        await ctx.send(embed=embed)

@bot.command()
async def itemdetails(ctx, item_id: int):
    try: 
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM items where id = %s", (item_id,))

        result = cur.fetchone()
        conn.close()

        if result:
            embed = discord.Embed(
                title=result[1],  # Item name as the title
                description="**Here are all the relevant statistics for your item!:**",  # Item lore as the description
                color=discord.Color.green()
            )
            embed.add_field(name = "Item Class: ", value = result[0], inline = False)
            embed.add_field(name = "Name: ", value = result[1], inline = False)
            embed.add_field(name = "ID File: ", value = result[3], inline = False)
            embed.add_field(name = "Lore: ", value = result[2], inline = False)
            embed.add_field(name = "ID File Extra: ", value = result[4], inline = False)
            embed.add_field(name = "ID: ", value = result[5], inline = False)
            embed.add_field(name = "Weight: ", value = result[6], inline = False)
            embed.add_field(name = "Attunable: ", value = result[7], inline = False)
            embed.add_field(name = "Price: ", value = result[8], inline = False)
            embed.add_field(name = "HP: ", value = result[9], inline = False)
            embed.add_field(name = "Mana: ", value = result[10], inline = False)
            embed.add_field(name = "Endurance: ", value = result[11], inline = False)
            embed.add_field(name = "AC: ", value = result[12], inline = False)
            embed.add_field(name = "Regen: ", value = result[13], inline = False)
            embed.add_field(name = "Mana Regen: ", value = result[14], inline = False)
            embed.add_field(name = "Classes: ", value = result[15], inline = False)
            embed.add_field(name = "Races: ", value = result[16], inline = False)
            embed.add_field(name = "Deity: ", value = result[17], inline = False)
            embed.add_field(name = "Recommended Level: ", value = result[18], inline = False)
            embed.add_field(name = "Required Skill: ", value = result[19], inline = False)

            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                title="Item Not Found",
                description="No item found with that ID. Please try again with a different ID.",
                color=discord.Color.red()
            )

            await ctx.send(embed=embed)

    except Exception as e:
        # Handle errors and send a embed message to the user
        embed = discord.Embed(
            title="Error Occurred in Processing Request 😔",
            description=f"An error occurred while processing your request: {str(e)}",
            color=discord.Color.red()
        )
        embed.add_field(
            name = "Please Try Again",
            value = "Make sure your question is clear and concise.",
            inline = False
        )
        embed.add_field(
            name = "Best Practices",
            value = "Try structuring your question like a Database query for best results. \n\nFor example, 'Find me a sword with a price less than 1000 platinum.'",
            inline = False
        )
        print(f"An error occurred: {str(e)}")

        await ctx.send(embed=embed)

        
keep_alive()
bot.run(DISCORD_BOT_TOKEN)
