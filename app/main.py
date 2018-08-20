# -*- coding: utf-8 -*-
import argparse
import telebot
from telebot import apihelper
import strings
import time
from googletrans import Translator


def rgt(text):
	translator = Translator()
	translation = text
	translation = translator.translate(translation, dest='ru', src='tg').text
	return translation


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
