import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.urandom(24)

    #DB_INFO = {
    #    'user': 'flaskuser',
    #    'password': 'tomo0118',
    #    'host': '127.0.0.1',
    #    'port': '5432',
    #    'name': 'flaskdb',
    #}
    #SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://{user}:{password}@{host}:{port}/{name}'.format(**DB_INFO)
    
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")  # ✅ アップロードフォルダを設定
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # ✅ 16MB のアップロード制限（オプション）

# デフォルトの食事リスト
DEFAULT_MEALS = [
    {"meal_title": "American 🍔", "meal_image": None},
    {"meal_title": "Barbecue 🍖", "meal_image": None},
    {"meal_title": "Chinese 🥡", "meal_image": None},
    {"meal_title": "French 🥖", "meal_image": None},
    {"meal_title": "Hamburger 🍟", "meal_image": None},
    {"meal_title": "Indian 🍛", "meal_image": None},
    {"meal_title": "Italian 🍝", "meal_image": None},
    {"meal_title": "Japanese 🍣", "meal_image": None},
    {"meal_title": "Mexican 🌮", "meal_image": None},
    {"meal_title": "Pizza 🍕", "meal_image": None},
    {"meal_title": "Seafood 🦞", "meal_image": None},
    {"meal_title": "Steak 🥩", "meal_image": None},
    {"meal_title": "Sushi 🍣", "meal_image": None},
    {"meal_title": "Thai 🍜", "meal_image": None},
]

# デフォルトのアクティビティリスト
DEFAULT_ACTIVITIES = [
    {"activity_title": "Wine & Cheese Night 🍷🧀", "activity_image": None},
    {"activity_title": "Binge-Watching Session 📺", "activity_image": None},
    {"activity_title": "Beach Day 🏖️", "activity_image": None},
    {"activity_title": "Hiking 🥾", "activity_image": None},
    {"activity_title": "Movie Date (Theater) 🎬", "activity_image": None},
    {"activity_title": "Bar Hopping 🍸", "activity_image": None},
    {"activity_title": "Shopping Date 🛍️", "activity_image": None},
    {"activity_title": "Museum Visit 🏛️", "activity_image": None},
    {"activity_title": "Study Date 📖", "activity_image": None},
    {"activity_title": "Long Drive 🚗", "activity_image": None},
]

# ✅ デフォルトの集合場所リスト
DEFAULT_MEETING_LOCATIONS = [
    {"location_title": "Host’s Place 🏡"},
    {"location_title": "Guest’s Place 🏠"},
]

# # デフォルトの食事リスト
# DEFAULT_MEALS = [
#     {"meal_title": "American 🍔", "meal_image": None},
#     {"meal_title": "Barbecue 🍖", "meal_image": None},
#     {"meal_title": "Chinese 🥡", "meal_image": None},
#     {"meal_title": "French 🥖", "meal_image": None},
#     {"meal_title": "Hamburger 🍟", "meal_image": None},
#     {"meal_title": "Indian 🍛", "meal_image": None},
#     {"meal_title": "Italian 🍝", "meal_image": None},
#     {"meal_title": "Japanese 🍣", "meal_image": None},
#     {"meal_title": "Mexican 🌮", "meal_image": None},
#     {"meal_title": "Pizza 🍕", "meal_image": None},
#     {"meal_title": "Seafood 🦞", "meal_image": None},
#     {"meal_title": "Steak 🥩", "meal_image": None},
#     {"meal_title": "Sushi 🍣", "meal_image": None},
#     {"meal_title": "Thai 🍜", "meal_image": None},
# ]

# # デフォルトのアクティビティリスト
# DEFAULT_ACTIVITIES = [
#     {"activity_title": "Wine & Cheese Night 🍷🧀", "activity_image": None},
#     {"activity_title": "Binge-Watching Session 📺", "activity_image": None},
#     {"activity_title": "Beach Day 🏖️", "activity_image": None},
#     {"activity_title": "Hiking 🥾", "activity_image": None},
#     {"activity_title": "Movie Date (Theater) 🎬", "activity_image": None},
#     {"activity_title": "Bar Hopping 🍸", "activity_image": None},
#     {"activity_title": "Shopping Date 🛍️", "activity_image": None},
#     {"activity_title": "Museum Visit 🏛️", "activity_image": None},
#     {"activity_title": "Study Date 📖", "activity_image": None},
#     {"activity_title": "Long Drive 🚗", "activity_image": None},
# ]
