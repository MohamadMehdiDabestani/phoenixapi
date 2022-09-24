import os
from telegram.ext import Updater, CommandHandler , MessageHandler , Filters


def login_command(update, context):
    update.message.reply_text("logoned")
    # print(update.message.chat.id)
    # print(update.message)
    context.bot.send_message(chat_id=808254824, # this line
                     text="a user sent request")

def command1(update, context):
    update.message.reply_text("comamnd")

print("port" , str(int(os.environ.get('PORT', 5000))))
def main():
    updater = Updater("5153591193:AAHeWKvCRVvZbvenaGyyae93ChWPzOeKZAM", use_context=True)
    dp = updater.dispatcher
    dp.bot.sendMessage(chat_id=808254824, text='I Started')
    echo_handler = MessageHandler(Filters.text & (~Filters.command), login_command)
    dp.add_handler(echo_handler)
    dp.add_handler(CommandHandler("login", login_command))
    dp.add_handler(CommandHandler("command1", command1))
    dp.add_handler(CommandHandler("command2", command1))
    dp.add_handler(CommandHandler("sayhi", command1))
    updater.start_webhook(listen="0.0.0.0",
                      port=int(os.environ.get('PORT', 5000)),
                      url_path="5153591193:AAHeWKvCRVvZbvenaGyyae93ChWPzOeKZAM",
                      webhook_url=  + "5153591193:AAHeWKvCRVvZbvenaGyyae93ChWPzOeKZAM"
                      )
    updater.idle()


main()
