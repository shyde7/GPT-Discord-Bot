# EverQuest Item Finder Bot

This project is a Discord bot designed to help users find items from the EverQuest game by leveraging the OpenAI API for natural language processing and PostgreSQL for data storage. The bot can understand user queries in natural language, translate them into SQL queries, and fetch relevant item data from the game's database.

## Features

- **Natural Language Understanding**: Users can type in natural language to find items in EverQuest.
- **Item Details**: Users can request detailed information about specific items by ID.
- **Data Richness**: Leverages PostgreSQL to store and retrieve vast amounts of item data.
- **Interactive Experience**: Provides an interactive experience on Discord with response pagination.
- **Web Interface**: Includes a Flask web server for additional functionality such as a dashboard or administrative controls.

## Tech Stack

- **HTML/CSS**: For creating a web interface and styling.
- **Python**: The core programming language used for the bot logic.
- **Flask**: A micro web framework for Python for running the web interface.
- **OpenAI API**: For processing natural language queries.
- **Discord API**: For interacting with Discord servers and channels.
- **PostgreSQL**: The relational database used for storing EverQuest item data.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.8 or higher
- pip
- PostgreSQL

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your-github-username/your-repo-name.git
cd your-repo-name
```

2. Install the following packages:

- pip install discord
- pip install discord.py
- pip install openai
- pip install psycopg2
- pip install asyncio
- pip install flask

3. Set up the environment variables:
   For macOS and Linux:

export DISCORD_BOT_TOKEN='your_discord_bot_token_here'
export OPENAI_API_KEY='your_openai_api_key_here'

4. Find the .txt file containing all items from [Lucy EQ](https://lucy.allakhazam.com), download this file and use it with the dbPopulator file and insert all the data into your own PostgreSQL Database.

5. Run the bot!
   Use: `python3 bot.py`

- This will run the flask server for the bot.
- Go to [localhost](http://localhost:8080) to invite the bot to your server
- Specify a channel ID for the bot, (use Discord developer mode)

### Usage

Once the bot is running and connected to your Discord server, you can use the following commands:

`!finditem <query> `- Searches for an item based on your query.

`!itemdetails <item_id>` - Retrieves detailed information about an item.

### Bot in Action

[Link to Youtube Vid of Bot Example](https://www.youtube.com/watch?v=oV4-e_GJgIk)
