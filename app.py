import feedparser
from telegram import Bot, InputFile
from telegram.constants import ParseMode
from pymongo import MongoClient
from urllib.parse import quote_plus
import time
import asyncio
import requests
from flask import Flask, jsonify
import random

app = Flask(__name__)

# Replace with your Telegram bot token
BOT_TOKEN = '6949865395:AAHegVxoroIvglqGgXJ5OgG0aFuCr7teJaU'

# Replace with the chat ID of your main Telegram channel for sending updates
UPDATE_CHANNEL_ID = '-1001999489910'

# Replace with the chat ID of your additional Telegram channel for storing processed URLs
CHANNEL_DB_ID = '-1002084765748'

# MongoDB configuration
MONGO_USERNAME = 'sandaruwan'
MONGO_PASSWORD = 'sahan@2005'
MONGO_CLUSTER_URL = 'cluster0.ixpjfdf.mongodb.net'
DATABASE_NAME = "rss_bot"
COLLECTION_NAME = "processed_urls"

# RSS feed URLs
RSS_FEED_URLS = [
    'https://feeds.arstechnica.com/arstechnica/index',
    'https://www.whathifi.com/feeds/all',
    'https://www.wired.com/feed/tag/ai/latest/rss',
    'https://www.digitaltrends.com/feed/',
    'https://mashable.com/feeds/rss/all'
]

# Escape username and password
escaped_username = quote_plus(MONGO_USERNAME)
escaped_password = quote_plus(MONGO_PASSWORD)

# MongoDB URI with escaped username and password
MONGO_URI = f"mongodb+srv://{escaped_username}:{escaped_password}@{MONGO_CLUSTER_URL}/{DATABASE_NAME}?retryWrites=true&w=majority"

# Set up MongoDB client and connect to the database
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DATABASE_NAME]
processed_urls_collection = db[COLLECTION_NAME]

async def send_message_async(chat_id, text, image_url=None):
    bot = Bot(token=BOT_TOKEN)

    if image_url:
        try:
            image_content = requests.get(image_url).content
            photo = InputFile(image_content, filename='image.jpg')
            await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Error sending photo: {e}")
    else:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)

def send_message_to_update_channel(text, image_url=None):
    asyncio.run(send_message_async(UPDATE_CHANNEL_ID, text, image_url=image_url))

def send_message_to_channel_db(text, image_url=None):
    asyncio.run(send_message_async(CHANNEL_DB_ID, text, image_url=image_url))

def check_duplicate_post(url):
    # Check if the URL is in the MongoDB collection
    return processed_urls_collection.count_documents({"url": url}) > 0

def mark_url_as_processed(url):
    # Add the URL to the MongoDB collection
    processed_urls_collection.insert_one({"url": url})

def parse_feed():
    max_retries = 3
    retry_delay = 5  # seconds
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Randomly select a feed from RSS_FEED_URLS
            selected_feed_url = random.choice(RSS_FEED_URLS)
            feed = feedparser.parse(selected_feed_url)
            entries = feed.entries

            if entries:
                for entry in entries:
                    title = entry.get('title', 'No Title')
                    link = entry.get('link', 'No Link')
                    description = entry.get('description', 'No Description')

                    # Check if the article has been processed
                    if check_duplicate_post(link):
                        continue

                    # Mark the article URL as processed
                    mark_url_as_processed(link)

                    # Extracting content from the entry
                    content = entry.get('content', [])
                    if content and 'value' in content[0]:
                        content_value = content[0]['value']
                        # Extracting the image URL from the content
                        image_url = content_value.split('<img')[1].split('src="')[1].split('"')[0] if '<img' in content_value else None
                    else:
                        image_url = None

                    # Construct the "Read More" URL
                    read_more_url = f"<a href='{link}'>Read More</a>"

                    if image_url:
                        # Send the message with the image to the update channel
                        message = f"<b>{title}</b>\n\n{description}\n\n{read_more_url}"
                        send_message_to_update_channel(message, image_url=image_url)
                    else:
                        # Send the message without the image to the update channel
                        message = f"<b>{title}</b>\n\n{description}\n\n{read_more_url}"
                        send_message_to_update_channel(message)

                        # If there is no image, also send the message to the additional channel
                        send_message_to_channel_db(message)

                    # Introduce a delay to avoid Telegram flood control
                    time.sleep(5)  # Adjust the delay time as needed

            break  # Break out of the loop if successful

        except Exception as e:
            # Send error messages to the database channel
            error_message = f"Error: {e}"
            send_message_to_channel_db(error_message)
            break  # Break out of the loop for other exceptions


@app.route('/')
def index():
    return "RSS Bot Web App is running!"

@app.route('/parse_feed', methods=['GET'])
def parse_feed_endpoint():
    parse_feed()
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
