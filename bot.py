import telebot
import config

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def welcome_message(message):
    bot.send_message(message.chat.id, "Приветствую, {0.first_name}.\n Я - бот <b>{1.first_name}</b>".format(message.from_user, bot.get_me()),
                     parse_mode='html')

bot.polling(none_stop=True)