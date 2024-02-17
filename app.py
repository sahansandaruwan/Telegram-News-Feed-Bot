import requests
import datetime
import time
import pymongo
import urllib.parse

# MongoDB connection details
MONGO_USERNAME = 'sandaruwan'
MONGO_PASSWORD = 'sahan@2005'
MONGO_DBNAME = 'telegram_bot_db'
MONGO_COLLECTION_NAME = 'user_ids'

# Telegram bot token
TOKEN = '6332932358:AAF8G5bFwIcVrOVnQ-uDDr_DWtwRInQijCc'
# Your Telegram user IDs
USER_IDS = ['5788265331', '6582839125']

# MongoDB connection URI
MONGO_URI = f"mongodb+srv://{urllib.parse.quote_plus(MONGO_USERNAME)}:{urllib.parse.quote_plus(MONGO_PASSWORD)}@cluster0.ixpjfdf.mongodb.net/{MONGO_DBNAME}?retryWrites=true&w=majority"

# Connect to MongoDB
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DBNAME]
collection = db[MONGO_COLLECTION_NAME]

def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    return response.json()

def save_user_id(user_id):
    # Check if the user ID already exists in the database
    existing_user = collection.find_one({"user_id": user_id})
    if not existing_user:
        # If user ID doesn't exist, insert it into the database
        collection.insert_one({"user_id": user_id})

def countdown():
    # Set your end date
    end_date = datetime.datetime(2024, 11, 30)  # End date: November 30, 2024
    start_date = datetime.datetime.now()
    total_days = (end_date - start_date).days
    progress_length = 20  # Adjust the length of the progress bar
    
    while True:
        try:
            # Calculate remaining time
            remaining_time = end_date - datetime.datetime.now()
            if remaining_time.days <= 0:
                for user_id in USER_IDS:
                    send_message(user_id, "Countdown ended!")
                break
            
            # Calculate percentage of time elapsed
            elapsed_days = (datetime.datetime.now() - start_date).days
            progress_percentage = int((elapsed_days / total_days) * 100)
            
            # Calculate number of completed progress bar segments
            completed_segments = int(progress_percentage / (100 / progress_length))
            
            # Construct the progress bar
            progress_bar = "▓" * completed_segments + "░" * (progress_length - completed_segments)
            
            # Send reminder message every day with progress bar
            for user_id in USER_IDS:
                send_message(user_id, f"Countdown reminder: {remaining_time.days} days left.\nProgress: {progress_percentage}%\n[{progress_bar}]")
            
            # Save user IDs to MongoDB to prevent duplicates
            for user_id in USER_IDS:
                save_user_id(user_id)
            
            # Wait for 24 hours before sending the next reminder
            time.sleep(86400)
        
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    countdown()
