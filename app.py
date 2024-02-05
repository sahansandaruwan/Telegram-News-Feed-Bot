import feedparser
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.constants import ParseMode
import logging
import asyncio
import requests
from urllib.error import URLError
import time

# Replace with your Telegram bot token
BOT_TOKEN = '6949865395:AAHegVxoroIvglqGgXJ5OgG0aFuCr7teJaU'

# Replace with the chat ID of your Telegram channel for sending updates
UPDATE_CHANNEL_ID = '-1001999489910'

# Replace with the URL of the RSS feed you want to monitor
RSS_FEED_URL = 'https://feeds.arstechnica.com/arstechnica/index'

# Set up logging to a file
logging.basicConfig(filename='rss_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set to store processed article URLs
processed_urls = set()

async def send_message_async(chat_id, text, image_url=None, keyboard=None):
    bot = Bot(token=BOT_TOKEN)
    
    if image_url:
        try:
            image_content = requests.get(image_url).content
            photo = InputFile(image_content, filename='image.jpg')
            await bot.send_photo(chat_id=chat_id, photo=photo, caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        except Exception as e:
            logging.error(f"Error sending photo: {e}")
    else:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

def send_message_to_update_channel(text, image_url=None, keyboard=None):
    asyncio.run(send_message_async(UPDATE_CHANNEL_ID, text, image_url=image_url, keyboard=keyboard))

def check_duplicate_post(url):
    # Check if the URL is in the processed set
    return url in processed_urls

def parse_feed():
    max_retries = 3
    retry_delay = 5  # seconds
    retry_count = 0
    urls_to_update_channel = []

    while retry_count < max_retries:
        try:
            feed = feedparser.parse(RSS_FEED_URL)
            entries = feed.entries
            logging.info(f"Number of entries in the feed: {len(entries)}")

            if entries:
                for entry in entries:
                    title = entry.get('title', 'No Title')
                    link = entry.get('link', 'No Link')
                    description = entry.get('description', 'No Description')
                    
                    # Check if the article has been processed
                    if check_duplicate_post(link):
                        continue

                    # Add the article URL to the processed set
                    processed_urls.add(link)
                    
                    # Extracting content from the entry
                    content = entry.get('content', [])
                    if content and 'value' in content[0]:
                        content_value = content[0]['value']
                        # Extracting the image URL from the content
                        image_url = content_value.split('<img')[1].split('src="')[1].split('"')[0] if '<img' in content_value else None
                    else:
                        image_url = None
                    
                    # Adjust the message formatting based on your needs
                    message = f"<b>{title}</b>\n\n{description}"
                    
                    # Inline keyboard for "Read More" button
                    inline_keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("Read More", url=link)]
                    ])

                    # Collect URLs for the update channel message
                    urls_to_update_channel.append(link)
                    
                    # Send the message with the image and inline button to the update channel
                    send_message_to_update_channel(message, image_url=image_url, keyboard=inline_keyboard)
                    
            else:
                logging.warning("No entries found in the feed.")

            logging.info("Feed content:\n" + str(feed))
            break  # Break out of the loop if successful

        except URLError as url_error:
            logging.error(f"URL Error: {url_error}")
            retry_count += 1
            logging.warning(f"Retrying in {retry_delay} seconds (Attempt {retry_count}/{max_retries})")
            time.sleep(retry_delay)

        except Exception as e:
            logging.error(f"Error: {e}")
            break  # Break out of the loop for other exceptions

    # Send the new URLs to the update channel
    if urls_to_update_channel:
        message = "\n".join(urls_to_update_channel)
        send_message_to_update_channel(message)

if __name__ == "__main__":
    while True:
        parse_feed()
        # Adjust the delay time (in seconds) based on your needs
        time.sleep(300)  # Check the feed every 5 minutes
