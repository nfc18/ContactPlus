"""Configuration for Contact Cleaner"""

import os
from datetime import datetime

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directories
BACKUP_DIR = os.path.join(BASE_DIR, 'backup')
DATA_DIR = os.path.join(BASE_DIR, 'data')
IMPORTS_DIR = os.path.join(BASE_DIR, 'Imports')

# Input file
SARA_VCARD_FILE = os.path.join(IMPORTS_DIR, 'Sara_Export_Sara A. Kerner and 3.074 others.vcf')

# Working files
REVIEW_QUEUE_FILE = os.path.join(DATA_DIR, 'review_queue.json')
DECISIONS_FILE = os.path.join(DATA_DIR, 'review_decisions.json')
PROCESSED_VCARD_FILE = os.path.join(DATA_DIR, f'Sara_Export_CLEANED_{datetime.now().strftime("%Y%m%d")}.vcf')

# Review thresholds
MAX_EMAILS_THRESHOLD = 4  # Flag contacts with 4 or more emails
MIN_NAME_LENGTH = 2       # Flag contacts with very short names

# Flask config
SECRET_KEY = 'dev-key-change-in-production'
DEBUG = True