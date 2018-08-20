# -*- coding: utf-8 -*-
import argparse
import telebot
from telebot import apihelper
import strings
import time
from googletrans import Translator
import re


def remove_emoji(text):
	emoji_pattern = re.compile("["
								u"\U0001F600-\U0001F64F"
								u"\U0001F300-\U0001F5FF"
								u"\U0001F680-\U0001F6FF"
								u"\U0001F1E0-\U0001F1FF"
								"]+", flags=re.UNICODE)

	return emoji_pattern.sub(r'', text)


def rgt(text):
	translator = Translator()
	f_text = remove_emoji(text)
	if f_text != '':
		translation = translator.translate(f_text, dest='ru', src='tg').text
		return translation
	return strings.error


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--socks', action='store', dest='s', help=strings.socks5_help)
parser.add_argument('-t', '--token', action='store', dest='t', help=strings.token_help)
args = parser.parse_args()

if args.s is not None:
	apihelper.proxy = {'https': 'socks5://' + args.s}

if args.t is None:
	print(strings.no_token)

bot = telebot.TeleBot(args.t)


@bot.message_handler(commands=['start'])
def a(message):
	bot.send_message(message.chat.id, strings.start)


@bot.message_handler(content_types=['text'])
def a(message):
	answer = rgt(message.text)
	bot.send_message(message.chat.id, answer)


while True:
	try:
		bot.polling(none_stop=True)
	except Exception as e:
		time.sleep(15)
