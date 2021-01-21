#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

"""

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import pytz
from datetime import time, timedelta

from PSQLpersist_dict import PsqlPersistence

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, PicklePersistence

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    output = "Test"
    update.message.reply_text(output)

CHAT_ID = 182072250

def callback_daily(context: CallbackContext):
    context.bot.send_message(chat_id=CHAT_ID,
                             text='Schon genommen?')


def check_msg(update: Update, context: CallbackContext):
    if ('yes' in update.message.text.lower()):
        user_name = update.effective_user.first_name
        context.user_data.update({"todayDone": True})
        reply_msg(True, user_name, update, context)
        context.dispatcher.update_persistence()
        context.dispatcher.persistence.flush()
        del user_name
    if ('no' in update.message.text.lower()):
        user_name = update.effective_user.first_name
        context.user_data.update({"todayDone": False})
        reply_msg(False, user_name, update, context)
        context.dispatcher.update_persistence()
        context.dispatcher.persistence.flush()
        launch_reminder(context, update)


def callback_remind_5(context: CallbackContext):
    context.bot.send_message(chat_id=context.job.context,
                             text='Did you do it now?')


def launch_reminder(context: CallbackContext, update: Update):
    context.job_queue.run_once(callback_remind_5, timedelta(minutes=5), context=update.message.chat_id)


def help_command(update: Update, context: CallbackContext) -> None:
    """ReminderBot, sends you a message to remind you of stuff."""
    update.message.reply_text('Help!')


def test_command(update: Update, context: CallbackContext) -> None:
    pass


def status_command(update: Update, context: CallbackContext) -> None:
    print("Context loaded:", context.dispatcher.persistence.get_user_data())
    if (bool(context.user_data)):
        print("CONTEXT: ", context.user_data)
        if "todayDone" in context.user_data and context.user_data["todayDone"]:
            update.message.reply_text(
                "Hello {}, you are already done for day.".format(update.message.from_user.first_name))
        else:
            update.message.reply_text(
                "Hello {}, you still have things to do!".format(update.message.from_user.first_name))
    else:
        update.message.reply_text("Hello {}. I have no status yet. Write me yes or no to get the status.".format(
            update.message.from_user.first_name))


def update_score(user_id, user_name, update: Update, context: CallbackContext) -> None:
    pass


'''if (not user_id in context.chat_data):
        backup_points = read_list()
        if(user_name in backup_points):
            context.chat_data[user_id] = {"name": user_name, "score": backup_points[user_name]}
            del backup_points
        else:
            context.chat_data[user_id] = {"name": user_name, "score": 0}
    else:
        context.chat_data[user_id].update({"name": user_name})
    if (context.chat_data.get(user_id) and context.chat_data.get(user_id).get("score")):
        context.chat_data[user_id]["score"] += 1
        update.message.reply_text(
            "GZ {}. Now you have {} points.".format(user_name, context.chat_data[user_id]["score"]))
    else:
        context.chat_data[user_id].update({"score": 1})
        update.message.reply_text("GZ {}. Now you have {} point.".format(update.message.from_user.first_name,
                                                                         context.chat_data[user_id]["score"]))
    print(context.chat_data)'''


def reply_msg(hasDone, user_name, update: Update, context: CallbackContext) -> None:
    if hasDone:
        update.message.reply_text("Good job {}.".format(update.message.from_user.first_name))
    else:
        update.message.reply_text("Pls remember {}.".format(update.message.from_user.first_name))


def read_token():
    f = open("token.txt", "r")
    token = str(f.readline()).strip()
    return token


def main():
    abc = PsqlPersistence()
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(read_token(), persistence=abc, use_context=True)

    job = updater.job_queue
    job_minute = job.run_daily(callback_daily,
                               time=time(20, 15, 00, tzinfo=pytz.timezone("Europe/Berlin")))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("leaderboard", start, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("points", start, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("status", status_command, ~Filters.update.edited_message))
    dispatcher.add_handler(CommandHandler("test", test_command, ~Filters.update.edited_message))
    # the actual messages to reply to
    dispatcher.add_handler(MessageHandler(~Filters.command & ~Filters.forwarded, check_msg, pass_job_queue=True))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
