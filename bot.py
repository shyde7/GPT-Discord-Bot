import discord
from discord.ext import commands
import os
import openai 

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")
CHANNEL_ID = 1225462283971330112

# Define the intents we want to use
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

# Initialize the OpenAI API client
openai.api_key = OPEN_AI_API_KEY




# Initialize the bot with the desired command prefix and intents
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event 
async def on_ready():
    print("Bot is ready")
    channel = bot.get_channel(CHANNEL_ID)  # Ensure you have the correct channel ID
    if channel:  # Check if channel was found
        embed = discord.Embed(
            title="Bot is ready!",
            description="I am now online and ready to help!",
            color=discord.Color.blurple()
        )
        await channel.send(embed=embed)
    else:
        print(f"Could not find channel with ID {CHANNEL_ID}")

@bot.command()
async def finditem(ctx, *, question: str):
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Find the item: {question}",
        max_tokens=100
    )
    await ctx.send(response.choices[0].text)


bot.run(BOT_TOKEN)