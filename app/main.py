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


def write_log(user_id, username, input_text, output_text):
	if username is not None:
		filename = 'logs/' + username + '.txt'
		log_file_hdr = strings.log_id + str(user_id) + '\n' + strings.log_username + username + '\n---\n\n'
	else:
		log_file_hdr = strings.log_id + str(user_id) + '\n---\n\n'
		filename = 'logs/' + str(user_id) + '.txt'
	if os.path.exists(filename):
		file = codecs.open(filename, 'a', 'utf-8')
	else:
		file = codecs.open(filename, 'w', 'utf-8')
		file.write(log_file_hdr)

	file.write(strings.log_text_in + input_text + '\n\n' + strings.log_text_out + output_text + '\n---\n\n')
	file.close()


def write_black_list(user_id):
	filename = 'blacklist/blacklist.txt'
	if not os.path.exists('blacklist'):
		os.mkdir('blacklist')
	file = codecs.open(filename, 'a', 'utf-8')
	file.write('\n' + user_id)
	file.close()


def remove_from_black_list(user_id):
	filename = 'blacklist/blacklist.txt'
	with open(filename) as f:
		file = f.read().split('\n')
	for i in range(len(file)):
		file[i] = re.sub(user_id, '', file[i])
	with open(filename, 'w') as f1:
		f1.writelines(['%s' % item for item in file])
	f1.close()


def is_banned(user_id):
	if os.path.exists('blacklist/blacklist.txt'):
		filename = 'blacklist/blacklist.txt'
		file = codecs.open(filename, 'r', 'utf-8')
		file_text = file.read()
		user_id = str(user_id)
		if user_id in file_text:
			file.close()
			return True
		else:
			file.close()
			return False
	else:
		return False


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


def random_result_check(answer):
	frequency = {}
	max_rp = 0
	text = answer
	text_l = text.lower()

	# Фильтр повторяющихся слов
	match_pattern = re.findall(r'\b[а-я]{4,99}\b', text_l)
	for word in match_pattern:
		count = frequency.get(word, 0)
		frequency[word] = count + 1
	frequency_list = frequency.keys()
	for words in frequency_list:
		rp = 0
		if frequency[words] > 1:
			rp = 1
		max_rp += rp
	if max_rp > 0:
		return False

	# Фильтр английских слов (не более 2-х в сообщении)
	eng = re.findall(r'\b[a-z]{1,99}\b', text_l)
	if len(eng) > 2:
		return False

	# Фильтр длинного набора букв и множества отдельных букв
	long_words = re.findall(r'\b[а-я,a-z]{17,99}\b', text_l)
	one_l = re.findall(r'\b[а-я,a-z]{1, 2}\b', text_l)
	if long_words or len(one_l) > 5:
		return False

	return True


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--socks', action='store', dest='s', help=strings.socks5_help)
parser.add_argument('-t', '--token', action='store', dest='t', help=strings.token_help)
parser.add_argument('-c', '--channel', action='store', dest='c', help=strings.channel_help)
parser.add_argument('-a', '--admin', action='store', dest='a', help=strings.admin_help)
parser.add_argument('-l', '--logs', action='store_true', dest='l', help=strings.logs_help)
args = parser.parse_args()

if args.s is not None:
	apihelper.proxy = {'https': 'socks5://' + args.s}

if args.t is None:
	print(strings.no_token_warning)

if args.l:
	logs = True
else:
	logs = False

if (args.a and args.c) is not None:
	repost_f = True
else:
	repost_f = False
	if (args.a or args.c) is not None:
		print(strings.channel_warning)

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

		att = 0
		while not random_result_check(answer):
			if att >= 8:
				break
			answer = random_text(message)
			att += 1

		if repost_f:
			ikb = types.InlineKeyboardMarkup()
			if message.chat.id == int(args.a):
				button_good = types.InlineKeyboardButton(text=strings.btn_good, callback_data='good_admin_s')
				button_bad = types.InlineKeyboardButton(text=strings.btn_bad, callback_data='bad_admin_s')
			else:
				button_good = types.InlineKeyboardButton(text=strings.btn_good, callback_data='good')
				button_bad = types.InlineKeyboardButton(text=strings.btn_bad, callback_data='bad')
			if not is_banned(message.chat.id):
				ikb.add(button_good, button_bad)
				bot.send_message(message.chat.id, answer, reply_markup=ikb)
			else:
				bot.send_message(message.chat.id, answer)
		else:
			bot.send_message(message.chat.id, answer)


@bot.callback_query_handler(func=lambda call: True)
def a(call):
	# Для пользователей
	if call.data == 'good':
		ikb = types.InlineKeyboardMarkup()
		button_good = types.InlineKeyboardButton(text=strings.btn_good_adm, callback_data='good_admin')
		button_bad = types.InlineKeyboardButton(text=strings.btn_bad_adm, callback_data='bad_admin')
		button_ban = types.InlineKeyboardButton(text=strings.btn_ban_adm + str(call.message.chat.id),
												callback_data='ban' + str(call.message.chat.id))
		ikb.add(button_good, button_bad, button_ban)
		bot.send_message(int(args.a), strings.admin_req_hdr + call.message.text, reply_markup=ikb)
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
							  text=call.message.text + strings.post_req + ' @' + args.c, reply_markup=None)
	if call.data == 'bad':
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
							  text=call.message.text, reply_markup=None)

	# Для админа
	if call.data == 'good_admin':
		rps = call.message.text.replace(strings.admin_req_hdr, '')
		bot.send_message('@' + args.c, rps)
		et = call.message.text.replace(strings.admin_req_hdr, strings.post_req_a_adm)
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
							  text=et, reply_markup=None)
	if call.data == 'bad_admin':
		et = call.message.text.replace(strings.admin_req_hdr, strings.post_req_d_adm)
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
							  text=et, reply_markup=None)

	if call.data == 'good_admin_s':
		bot.send_message('@' + args.c, call.message.text)
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
							  text=call.message.text + strings.post_adm, reply_markup=None)
	if call.data == 'bad_admin_s':
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
							  text=call.message.text, reply_markup=None)

	if call.data[0:3] == 'ban':
		ban_id = call.data
		ban_id = re.sub(r'[ban]', '', ban_id)
		write_black_list(ban_id)
		ikb = types.InlineKeyboardMarkup()
		button_unban = types.InlineKeyboardButton(text=strings.btn_unban_adm, callback_data='unban' + ban_id)
		ikb.add(button_unban)
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
							  text=strings.admin_banned_1 + ban_id + strings.admin_banned_2, reply_markup=ikb)
	if call.data[0:5] == 'unban':
		unban_id = call.data
		unban_id = re.sub(r'[unba]', '', unban_id)
		remove_from_black_list(unban_id)
		ikb = types.InlineKeyboardMarkup()
		button_ban = types.InlineKeyboardButton(text=strings.btn_ban_adm, callback_data='ban' + unban_id)
		ikb.add(button_ban)
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
							  text=strings.admin_banned_1 + unban_id + strings.admin_unbanned_2, reply_markup=ikb)


while True:
	try:
		bot.polling(none_stop=True)
	except Exception as e:
		time.sleep(15)
