import configparser
import logging
import os
import sys
from datetime import datetime
from decimal import Decimal, getcontext

import nano
import requests

import qrcode
import telegram
import zbarlight
from PIL import Image

from . import currency, db

# Read config and parse constants
config = configparser.ConfigParser()
config.read(os.environ['MY_CONF_DIR'] + '/webhooks.ini')
logging.basicConfig(handlers=[logging.StreamHandler()], level=logging.INFO)
# Telegram API
TELEGRAM_KEY = config.get('webhooks', 'telegram_key')

# Constants
MIN_TIP = config.get('webhooks', 'min_tip')
NODE_IP = config.get('webhooks', 'node_ip')
BOTNAME = config.get('webhooks', 'bot_id_telegram')

# Connect to Telegram
telegram_bot = telegram.Bot(token=TELEGRAM_KEY)


def read_qr(qr_image):
    codes = zbarlight.scan_codes('qrcode', qr_image)
    return codes


def write_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def get_photo(message):
    file_id = max(message, key=lambda x: x['file_size']).get('file_id')
    image = telegram_bot.get_file(file_id)
    image_url = image.file_path
    img_data = requests.get(image_url).content
    return img_data


def process(photos):
    pass
