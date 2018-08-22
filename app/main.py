# -*- coding: utf-8 -*-
import argparse
import telebot
from telebot import apihelper
from telebot import types
import strings
import time
from googletrans import Translator
import re
import os
import codecs
import random


def write_log(message_id, username, input_text, output_text):
	filename = 'logs/' + username + '.txt'
	if os.path.exists(filename):
		file = codecs.open(filename, 'a', 'utf-8')
	else:
		file = codecs.open(filename, 'w', 'utf-8')
		file.write(strings.log_id + str(message_id) + '\n' + strings.log_username + username + '\n---\n\n')

	file.write(strings.log_text_in + input_text + '\n\n' + strings.log_text_out + output_text + '\n---\n\n')
	file.close()


def remove_emoji(text):
	emoji_pattern = re.compile("["
								u"\U0001F600-\U0001F64F"
								u"\U0001F300-\U0001F5FF"
								u"\U0001F680-\U0001F6FF"
								u"\U0001F1E0-\U0001F1FF"
								"]+", flags=re.UNICODE)

	return emoji_pattern.sub(r'', text)


def user_text(message):
	f_text = remove_emoji(message.text)
	if f_text != '':
		translation = translator.translate(f_text, dest='ru', src='tg').text
		if logs:
			write_log(message.chat.id, message.chat.username, f_text, translation)
		return translation
	return strings.error


def random_generator():
	vow = 'аеиоуыэюя'
	cons = 'бвгджзйклмнпрстфхцчшщ'

	random_str = ''
	while len(random_str) < random.randint(80, 200):
		v = ''.join(random.choice(vow) for x in range(random.randint(1, 3)))
		c = ''.join(random.choice(cons) for x in range(random.randint(1, 2)))

		if bool(random.getrandbits(1)):
			s = ' '
		else:
			s = ''

		random_str += v + c + s
	return random_str


def random_text(message):
	rt = random_generator()
	translation = translator.translate(rt, dest='ru', src='tg').text
	if logs:
		write_log(message.chat.id, message.chat.username, rt, translation)
	return translation

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--socks', action='store', dest='s', help=strings.socks5_help)
parser.add_argument('-t', '--token', action='store', dest='t', help=strings.token_help)
parser.add_argument('-c', '--channel', action='store', dest='c', help=strings.channel_help)
parser.add_argument('-l', '--logs', action='store_true', dest='l', help=strings.logs_help)
args = parser.parse_args()

if args.s is not None:
	apihelper.proxy = {'https': 'socks5://' + args.s}

if args.t is None:
	print(strings.no_token)

if args.l:
	logs = True
else:
	logs = False

bot = telebot.TeleBot(args.t)

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(strings.keyboard_random)

translator = Translator()

if logs:
	if not os.path.isdir('logs'):
		os.mkdir('logs')


@bot.message_handler(commands=['start'])
def a(message):
	str_start = strings.start
	if logs:
		str_start += '\n' + strings.log_warning
	bot.send_message(message.chat.id, str_start, reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def a(message):
	if message.text != strings.keyboard_random:
		answer = user_text(message)
		bot.send_message(message.chat.id, answer, reply_markup=keyboard)
	else:
		answer = random_text(message)
		if args.c is not None:
			ikb = types.InlineKeyboardMarkup()
			button_good = types.InlineKeyboardButton(text=strings.btn_good, callback_data='good')
			button_bad = types.InlineKeyboardButton(text=strings.btn_bad, callback_data='bad')
			ikb.add(button_good, button_bad)
			bot.send_message(message.chat.id, answer, reply_markup=ikb)
		else:
			bot.send_message(message.chat.id, answer)


@bot.callback_query_handler(func=lambda call: True)
def a(call):
	if call.data == 'good':
		bot.send_message('@' + args.c, call.message.text)
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
							  text=call.message.text + strings.posted, reply_markup=None)
	if call.data == 'bad':
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
							  text=call.message.text, reply_markup=None)

while True:
	try:
		bot.polling(none_stop=True)
	except Exception as e:
		time.sleep(15)
