import telebot
import config
import requests
import bs4
import re
import datetime

from telebot import types

def get_schedule_by_group(group: str):
    facult = ['yuf', 'rtf', 'rkf', 'fet', 'fsu', 'fvs', 'gf', 'fb', 'ef', 'pish']
    if not group[0].isdigit():
        return 'Номер группы введен неверно'
    group = group.lower()
    response = requests.get(
        f'https://timetable.tusur.ru/faculties/{facult[int(group[0])]}/groups/{group}')
    lessons = bs4.BeautifulSoup(response.content, 'html.parser')
    lessons = lessons.find_all('tr', {'class': re.compile('lesson')})
    if lessons == []:
        return 'Пар нет или номер группы введен неверно'
    for i in range(7):
        lessons[i] = lessons[i].find_all('td')
    result_string = ''
    time_mas = ['8:50', '10:40', '13:15', '15:00', '16:45', '18:30', '20:15']
    today = datetime.datetime.today().weekday()
    if today == 6:
         return 'Сегодня воскресенье'
    for i in range(7):
            data = lessons[i][today].find('div', {'class': 'hidden for_print'})
            if data is None:
                continue
            result_string += time_mas[i]
            data = data.find_all('span')
            result_string += f'\nПредмет: {data[0].text}'
            result_string += f'\nТип пары: {data[1].text}'
            result_string += f'\nАудитория: {data[2].text}'
            result_string += f'\nПреподаватель: {data[3].text}'
            result_string += '\n'
            result_string += '\n'
    if result_string == '':
         return 'Сегодня пар нет'
    return result_string

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def welcome_message(message):
    welcome_img = open('welcome.png','rb')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Узнать расписание на сегодня")
    markup.add(item1)
    bot.send_message(message.chat.id, 'Приветствую, {0.first_name}.\n Я - бот <b>{1.first_name}</b>.\nЧтобы узнать расписание введите "Узнать расписание на сегодня" или нажмите на кнопку ниже'.format(message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)
    bot.send_photo(message.chat.id, welcome_img)
    
@bot.message_handler(func=lambda message: True)
def timefind_out_the_schedule(message):
    if message.text=='Узнать расписание на сегодня':
        markup = telebot.types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Введите номер группы',reply_markup=markup)
        bot.register_next_step_handler(message,handle_group_number)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Узнать расписание на сегодня")
        markup.add(item1)
        bot.send_message(message.chat.id,'Я не знаю, что ответить.\nЧтобы узнать расписание нажмите на кнопку ниже',reply_markup=markup)

def handle_group_number(message):
    timetable = get_schedule_by_group(message.text)
    bot.send_message(message.chat.id,timetable)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Узнать расписание на сегодня")
    markup.add(item1)
    bot.send_message(message.chat.id, 'Если хотите узнать расписание еще раз или расписание другой группы нажмите на кнопку "Узнать расписание на сегодня"',reply_markup=markup)




bot.polling(none_stop=True)