import discord
from discord.ext import commands

BOT_TOKEN = "BOT_TOKEN"
CHANNEL_ID = 1225462283971330112

# Define the intents we want to use
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True


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

# A simple command responding to "!hello"
@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()  # Added parentheses to make this a proper decorator
async def ping(ctx):
    await ctx.send('Pong!')

bot.run(BOT_TOKEN)