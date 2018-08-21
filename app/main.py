# -*- coding: utf-8 -*-
import argparse
import telebot
from telebot import apihelper
import strings
import time
from googletrans import Translator
import re
import os


def write_log(message_id, username, input_text, output_text):
	filename = 'logs/' + username + '.txt'
	if os.path.exists(filename):
		file = open(filename, 'a')
	else:
		file = open(filename, 'w')
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


def rgt(message):
	translator = Translator()
	f_text = remove_emoji(message.text)
	if f_text != '':
		translation = translator.translate(f_text, dest='ru', src='tg').text
		if logs:
			write_log(message.chat.id, message.chat.username, f_text, translation)
		return translation
	return strings.error


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--socks', action='store', dest='s', help=strings.socks5_help)
parser.add_argument('-t', '--token', action='store', dest='t', help=strings.token_help)
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

if logs:
	if not os.path.isdir('logs'):
		os.mkdir('logs')


@bot.message_handler(commands=['start'])
def a(message):
	str_start = strings.start
	if logs:
		str_start += '\n' + strings.log_warning
	bot.send_message(message.chat.id, str_start)


@bot.message_handler(content_types=['text'])
def a(message):
	answer = rgt(message)
	bot.send_message(message.chat.id, answer)


while True:
	try:
		bot.polling(none_stop=True)
	except Exception as e:
		time.sleep(15)
