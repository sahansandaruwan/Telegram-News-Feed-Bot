# Telegram News Feed Bot

## Overview
The Telegram News Feed Bot is a Python application that fetches news articles from various RSS feeds and shares them on Telegram channels. It periodically checks the RSS feeds, retrieves new articles, and publishes them to designated channels. The bot utilizes asynchronous programming with asyncio for efficient message sending and integrates with MongoDB to keep track of processed URLs and prevent duplicate posts.

## How It Works

### The bot operates as follows:

1. **Fetching RSS Feeds**: The application is configured with a list of RSS feed URLs from various sources like news websites and tech blogs.
2. **Parsing Feeds**: It randomly selects a feed from the configured list and parses the XML data using the feedparser library to extract article metadata such as title, link, and description.
3. **Checking for Duplicates**: Before posting an article, the bot checks if the article's URL has been processed before to avoid duplicate posts. It maintains a MongoDB database to store processed URLs.
4. **Sending Messages**: Once a new article is identified, the bot constructs a message containing the article's title, description, and a "Read More" link. If available, it also includes the article's image. The message is then sent to the main Telegram channel designated for updates.
5. **Additional Channel**: Optionally, the bot can send the same message to an additional channel for archiving or backup purposes.
6. **Web Interface (Optional)**: The bot includes a Flask web server to provide an endpoint for manually triggering the feed parsing process.

## Configuration

### To set up and configure the Telegram News Feed Bot, follow these steps:

1. **Telegram Bot Token**: Replace the **BOT_TOKEN** variable in the code with your Telegram bot token obtained from the BotFather.
2. **Telegram Channel IDs**: Replace **UPDATE_CHANNEL_ID** and **CHANNEL_DB_ID** with the chat IDs of your main Telegram channel for sending updates and the additional channel for storing processed URLs, respectively.
3. **MongoDB Configuration**: Provide your MongoDB credentials (username, password, cluster URL) and configure the database and collection names.
4. **RSS Feed URLs**: Customize the **RSS_FEED_URLS** list with the URLs of the RSS feeds you want to monitor.
5. **Dependencies**: Install the required Python dependencies listed in **requirements.txt using pip install -r requirements.txt.**
6. **Run the Bot**: Execute the Python script **(bot.py)** to start the bot. Optionally, deploy the bot to a server for continuous operation.

## Usage

Once configured and running, the bot will automatically fetch news articles from the specified RSS feeds and share them on the designated Telegram channels at regular intervals. You can manually trigger the feed parsing process by accessing the provided web interface endpoint.
