import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8179000491:xxx")

API_ID = int(os.environ.get("API_ID", "27396410"))

API_HASH = os.environ.get("API_HASH", "175dd5dc67ce353d41d7aefd5a104d9c")

ADMINS = int(os.environ.get("ADMINS", "6454380944"))

ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))