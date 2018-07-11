# -*- coding: utf-8 -*-
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import wp
import logging
import os



current_directory = os.getcwd()
data = []
title = ""

TITLE, NEWARTICLE, PREVIEW = range(3)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


logger = logging.getLogger(__name__)

def start(bot, update):
    reply_keywords = [['/cancel', '/finish']] # show all post, view a specific post?
    update.message.reply_text(
        'Hi! My name is wpPublish_Bot. I will help you publish wordpress post by simply sending and/or forwarding messages to me.'
        'Send /cancel to discard the post or /finish to post the messages on your website.\n\n',
        reply_markup=ReplyKeyboardMarkup(reply_keywords, one_time_keyboard=True))

    return TITLE

def get_title(bot, update):
    global title
    title = update.message.text
    update.message.reply_text('Now send me some messages...')
    return NEWARTICLE

def new_photo(bot, update):
    user = update.message.from_user
    photo_file = bot.get_file(update.message.photo[-1].file_id)
    filename = ""
    i = 0
    while True:
        filename = 'photo' + str(i) + '.jpg'
        if os.path.isfile(filename) == False:
            photo_file.download(filename)
            data.append(current_directory + '/' + filename)
            break
        i += 1
    return NEWARTICLE

def new_text(bot,update):
    message = update.message.text
    data.append(message)
    return NEWARTICLE

def post_article(bot, update):
    wp.post_article(data, title)
    update.message.reply_text('Article posted!', reply_markup=ReplyKeyboardMarkup([['/start']], one_time_keyboard=True))
    data.clear()
    return ConversationHandler.END

def finish(bot, update):
    global title
    update.message.reply_text(
        'This is the preview',
        reply_markup=ReplyKeyboardMarkup([['/yes', '/no']], one_time_keyboard=True))
    # send preview
    update.message.reply_text(title)
    for d in data:
        if d.startswith('/home') == True:
            bot.send_photo(update.message.chat.id, photo=open(d, 'rb'))
        else:
            update.message.reply_text(d)
    update.message.reply_text('Is it ok?')
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

def main():
    updater = Updater('TOKEN')
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
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

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
