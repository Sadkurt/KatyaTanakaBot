from __future__ import unicode_literals

import logging
import os
from uuid import uuid4

from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from pybooru import Danbooru


PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.environ["TOKEN"]
DUSERNAME = os.environ["DUSERNAME"]
DAPIKEY = os.environ["DAPIKEY"]
client = Danbooru('danbooru', username=DUSERNAME, api_key=DAPIKEY)


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def help_command(update, context):
    update.message.reply_text('Я вхожу в данбору без стука! \danb моя команда - шнырь!')

def choose(update, context):
    query = update.inline_query.query
    tags = client.tag_list(name_matches=query+'*')
    results = []



    for tag in tags:

        thumbimg = ''
        posts = client.post_list(tags=tag['name'], limit=1)
        if not posts:
            print("Пустой запрос")
            message = "Пустой запрос"
        else:
            for post in posts:
                if "file_url" in post:
                    print(post["id"])
                    thumbimg = str(post["preview_file_url"])
                    message = str(post["large_file_url"])
                else:
                    message = "Нету ссылки или забанен"


        results.append(InlineQueryResultArticle(
                        id=uuid4(),
                        title=tag['name'],
                        thumb_url=thumbimg,
                        input_message_content=InputTextMessageContent(message)))

    update.inline_query.answer(results)

def danb(update, context):
    posts = client.post_list(tags=str(context.args[0]), limit=1)
    if not posts:
        update.message.reply_text("Пустой запрос")
    else:
        for post in posts:
            if "file_url" in post:
                update.message.reply_text(str(post["large_file_url"]))
            else:
                update.message.reply_text("Нету ссылки или забанен")


def main():

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help_command))
    # dp.add_handler(CommandHandler("danb", danb, pass_args=True))
    dp.add_handler(InlineQueryHandler(choose))

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://tgbotkatya.herokuapp.com/' + TOKEN)

    updater.idle()


if __name__ == '__main__':
    main()