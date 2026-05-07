import os
import time
import schedule
import requests
import telebot
from openai import OpenAI

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY")
CHANNEL = "@first_ai_channe1"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENROUTER_KEY, base_url="https://openrouter.ai/api/v1")

def get_news():
    topics = ["science", "technology", "history"]
    import random
    topic = random.choice(topics)
    url = f"https://newsapi.org/v2/everything?q={topic}&language=ru&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
    res = requests.get(url).json()
    articles = res.get("articles", [])
    if articles:
        return random.choice(articles)
    return None

def get_photo(query):
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_KEY}"
    res = requests.get(url).json()
    return res.get("urls", {}).get("regular", None)

def write_post(article):
    prompt = f"""Напиши интересный пост для Telegram канала на русском языке на основе этой новости:
Заголовок: {article['title']}
Описание: {article['description']}

Пост должен быть:
- Интересным и engaging
- 3-5 предложений
- С эмодзи
- С хештегами в конце"""

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def publish_post():
    try:
        article = get_news()
        if not article:
            return
        
        post_text = write_post(article)
        if not post_text or not post_text.strip():
            return

        query = article.get("title", "science technology")
        photo_url = get_photo(query)

        if photo_url:
            bot.send_photo(CHANNEL, photo_url, caption=post_text)
        else:
            bot.send_message(CHANNEL, post_text)

        print(f"✅ Пост опубликован!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# Расписание — 12 постов в день каждые 2 часа
schedule.every(2).hours.do(publish_post)

# Первый пост сразу при запуске
publish_post()

print("🤖 Бот запущен!")
while True:
    schedule.run_pending()
    time.sleep(60)