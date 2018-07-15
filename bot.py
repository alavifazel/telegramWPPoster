# -*- coding: utf-8 -*-
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import wp
import logging
import os
from wordpress_xmlrpc.exceptions import InvalidCredentialsError
from urllib.parse import quote
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")


current_directory = os.getcwd()
data = []
authenticated_users = []
title = ""
rhash = "" # optional
USER, PASS, TITLE, NEWARTICLE, PREVIEW = range(5)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


logger = logging.getLogger(__name__)

def start(bot, update):
    reply_keyword = [['/start']]
    #show all post, view a specific post?
    logger.info(update.message.chat.id)
    if update.message.chat.id not in authenticated_users:
        update.message.reply_text(
            "Enter username:", reply_markup=ReplyKeyboardRemove())

        return USER
    else:
        update.message.reply_text("Send me the title...")
        return TITLE

def get_title(bot, update):
    global title
    title = update.message.text
    reply_keywords = [['/cancel', '/finish']]
    update.message.reply_text("Now send me some messages...\n"
                              "When you are done, submit with /finish or cancel with /cancel .\n",
                              reply_markup=ReplyKeyboardMarkup(reply_keywords, one_time_keyboard=True))
    return NEWARTICLE

def new_photo(bot, update):
    user = update.message.from_user
    photo_file = bot.get_file(update.message.photo[-1].file_id)
    filename = ""
    i = 0
    while True:
        filename = "photo" + str(i) + ".jpg"
        if os.path.isfile(filename) == False:
            photo_file.download(filename)
            data.append(current_directory + "/" + filename)
            break
        i += 1
    return NEWARTICLE

def new_text(bot,update):
    message = update.message.text
    data.append(message)
    return NEWARTICLE

def post_article(bot, update):
    url = wp.post_article(data, title)
    update.message.reply_text("Post has been published!", reply_markup=ReplyKeyboardMarkup([['/start']], one_time_keyboard=True))
    # for telegram Instant View (IV)
    if not rhash:
        update.message.reply_text(url)
    else:
        update.message.reply_text("https://t.me/iv?url=" + quote(url, safe='') + "&rhash=" + rhash)
    data.clear()
    return ConversationHandler.END

def finish(bot, update):
    global title
    update.message.reply_text(
        "Showing preview now...",
        reply_markup=ReplyKeyboardMarkup([['/yes', '/no']], one_time_keyboard=True))
    # send preview
    update.message.reply_text(title)
    for d in data:
        if d.startswith('/home') == True:
            bot.send_photo(update.message.chat.id, photo=open(d, 'rb'))
        else:
            update.message.reply_text(d)
    update.message.reply_text("Is it correct?")
    return PREVIEW

def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Cancelled',
                              reply_markup=ReplyKeyboardMarkup([['/start']], one_time_keyboard=True))
    data.clear()
    return ConversationHandler.END


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def get_user(bot, update):
    update.message.reply_text("Enter password:")
    global username
    username = update.message.text
    return PASS

def get_pass(bot, update):
    global password
    password = update.message.text
    chat_id = update.message.chat.id
    if chat_id not in authenticated_users:
        try:
            wp.auth(username, password)
            authenticated_users.append(chat_id)
        except InvalidCredentialsError:
            update.message.reply_text("Invalid Credentials.\n\n"
                                      "Start the bot with /start to try again.",
                                      reply_markup=ReplyKeyboardMarkup([['/start']], one_time_keyboard=True))
            return ConversationHandler.END
        update.message.reply_text("Login succesful!\n")
    update.message.reply_text("Send me the title")

    return TITLE    

def main():
    updater = Updater(config["INFOS"]["Token"])
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USER: [RegexHandler('(.*?)', get_user)],
            PASS: [RegexHandler('(.*?)', get_pass)],
            TITLE: [RegexHandler('^(?!.*(/cancel))', get_title)],
            NEWARTICLE: [MessageHandler(Filters.photo, new_photo), RegexHandler('^(?!.*(/finish|/cancel))', new_text),
                    CommandHandler('finish', finish)],
            PREVIEW: [CommandHandler('yes', post_article), CommandHandler('no', cancel)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
