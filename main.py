from __future__ import unicode_literals

import logging
import os
import random
from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent,\
                     InlineQueryResultPhoto, InlineQueryResultGif, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from pybooru import Danbooru


PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ["TOKEN"]
DUSERNAME = os.environ["DUSERNAME"]
DAPIKEY = os.environ["DAPIKEY"]

updater = Updater(TOKEN, use_context=True)
client = Danbooru('danbooru', username=DUSERNAME, api_key=DAPIKEY)
bot = Bot(TOKEN)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def main():

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("random", random_command))
    dp.add_handler(CommandHandler("gif", gif_command))
    dp.add_handler(InlineQueryHandler(choose))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://tgbotkatya.herokuapp.com/' + TOKEN)

    updater.idle()


def help_command(update, context):
    update.message.reply_text('Я вхожу в данбору без стука!  моя команда - шнырь!')


def random_command(update, context):
    posts = client.post_list(random=True, limit=3)
    message = "Не получилось, попробуй еще разок ^_^"
    if not posts:
        print("Пустой запрос")
    else:
        for post in posts:
            if "file_url" in post:
                message = f"[Линк]({str(post['large_file_url'])})"
    update.message.reply_markdown(message)


def gif_command(update, context):
    posts = client.post_list(tags="animated_gif", limit=3, random=True)
    if not posts:
        message = "Не получилось, попробуй еще разок ^_^"
    else:
        for post in posts:
            if "file_url" in post:

                message = str(post['large_file_url'])
    bot.send_animation(chat_id=update.message.chat_id, animation=message)


def fetch_posts_by_tags(tags):
    results = []
    for tag in tags:
        posts = client.post_list(tags=tag['name'], limit=10)
        if not posts:
            print("Пустой запрос")
        else:
            post = random.choice(posts)
            if "file_url" in post:
                print(post["id"])
                thumbimg = str(post["preview_file_url"])
                message = str(post["large_file_url"])
                results.append(InlineQueryResultPhoto(
                    id=uuid4(),
                    title='RANDOM',
                    photo_width=150,
                    photo_height=150,
                    thumb_url=thumbimg,
                    photo_url=message))
    return results


def fetch_animated_post():
    results = []
    posts = client.post_list(tags="animated_gif", limit=10, random=True)
    if not posts:
        print("Пустой запрос")
    else:
        for post in posts:
            if "file_url" in post:
                print(post["id"])
                thumbimg = str(post["preview_file_url"])
                message = str(post["large_file_url"])
                results.append(InlineQueryResultGif(
                    id=uuid4(),
                    gif_width=150,
                    gif_height=150,
                    thumb_url=thumbimg,
                    gif_url=message))
    return results


def fetch_random_post():
    results = []
    posts = client.post_list(random=True, limit=10)
    if not posts:
        print("Пустой запрос")
    else:
        for post in posts:
            if "file_url" in post:
                print(post["id"])
                thumbimg = str(post["preview_file_url"])
                message = str(post["large_file_url"])
                results.append(InlineQueryResultPhoto(
                    id=uuid4(),
                    title='RANDOM',
                    photo_width=150,
                    photo_height=150,
                    thumb_url=thumbimg,
                    photo_url=message))
    return results


def choose(update, context):
    query = update.inline_query.query
    if query == "random":
        results = fetch_random_post()
    elif query == "gif":
        results = fetch_animated_post()
    else:
        tags = client.tag_list(name_matches=query + '*')
        results = fetch_posts_by_tags(tags)
    update.inline_query.answer(results, cache_time=1)


if __name__ == '__main__':
    main()
