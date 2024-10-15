# scraping/telegram_scraper.py

import os
import csv
import logging
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import MessageMediaPhoto

# Ensure logs directory exists
os.makedirs('scraping/logs', exist_ok=True)

# Set up logging
logging.basicConfig(filename='scraping/logs/telegram_scraper.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

# load env variables

load_dotenv()


api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')

# Initialize Telegram client
client = TelegramClient('new_session_name', api_id, api_hash)

async def scrape_channel(channel, collect_images=False):
    """
    Scrapes messages from a specified Telegram channel.

    Args:
        channel (str): The Telegram channel URL.
        collect_images (bool): Whether to download images from the messages.

    Returns:
        None
    """
    try:
        await client.start(phone)
        logging.info(f'Successfully connected to Telegram for channel: {channel}')
        
        # Get messages from the channel
        messages = await client.get_messages(channel, limit=100)  # Adjust limit as needed
        
        # Ensure data directories exist
        os.makedirs('scraping/data/raw', exist_ok=True)
        if collect_images:
            os.makedirs('scraping/data/raw/media', exist_ok=True)
        
        csv_filename = f'scraping/data/raw/{channel.replace("https://t.me/", "")}.csv'
        with open(csv_filename, mode='w', encoding='utf-8') as file:
            writer = csv.writer(file)
            if collect_images:
                writer.writerow(['message_id', 'date', 'sender_id', 'message', 'media_path'])
            else:
                writer.writerow(['message_id', 'date', 'sender_id', 'message'])
            
            for message in messages:
                media_path = None
                if collect_images and message.media and isinstance(message.media, MessageMediaPhoto):
                    media_path = f'scraping/data/raw/media/{message.id}.jpg'
                    await message.download_media(media_path)
                if collect_images:
                    writer.writerow([message.id, message.date, message.sender_id, message.message, media_path])
                else:
                    writer.writerow([message.id, message.date, message.sender_id, message.message])
                
        logging.info(f'Successfully scraped and saved data for channel: {channel}')
        
    except SessionPasswordNeededError:
        logging.error('Session password is needed. Please check your credentials and try again.')
    except Exception as e:
        logging.error(f'Error scraping channel {channel}: {str(e)}')

if __name__ == '__main__':
    channels = [
        'https://t.me/DoctorsET',
        'https://t.me/lobelia4cosmetics',
        'https://t.me/yetenaweg',
        'https://t.me/EAHCI',
        'https://et.tgstat.com/medicine'
    ]
    
    image_channels = [
        'https://t.me/Chemed',
        'https://t.me/lobelia4cosmetics'
    ]
    
    with client:
        # Scrape messages from all channels
        for channel in channels:
            client.loop.run_until_complete(scrape_channel(channel))
        
        # Scrape images from specific channels
        for channel in image_channels:
            client.loop.run_until_complete(scrape_channel(channel, collect_images=True))