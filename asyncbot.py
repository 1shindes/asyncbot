#! /usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import requests
import orjson
import json
import os
import shutil #for rmtree()
import datetime
from telebot import types

''' -------- secrets ---------- '''
#TODO put'em into .env
API_KEY=''
#Bearer token for REST API
token = 'b74f219a6644d9650e155e7139add0a80ffd519e'
''' -------- constants/variables ---------- '''
gkhplus_server = 'delta.gkh.plus'
base_url = 'https://' + gkhplus_server + '/'
tgdload_url = 'https://api.telegram.org/file/bot' + API_KEY + '/'
post_headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json"
        }
UK_phone = '+70000000000'
UK_name = 'ООО "УК Техстрой"'
max_req_num = 99 # max requestnumber
### emojiii.iii
disappointed = '\U0001F61E'
upset = disappointed 
wink = '\U0001F609'
rolling = '\U0001F644'
celebrate = '\U0001F389'
expressionless = '\U0001F611'
hug = '\U0001F917'
robot = '\U0001F916'
writing_hand = '\u270D'
hourglass = '\u23F3'
excl_white = '\u2755'
shouting_head = '\U0001F5E3'
open_book = '\U0001F4D6'
green_check = '\u2705'
play = '\u25B6'
pause = '\u23F8'
blue_dia = '\U0001F539'

''' ============== classes ============= '''
class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, req):
        req.headers["Authorization"] = "Bearer " + self.token
        return req
class House:
    def __init__(self, street, bld, house_id):
        self.street = street
        self.bld = bld
        self.house_id = house_id
#    def __repr__(self):
#        return '({street}; {bld})'.format(street=self.street, bld=self.bld)
class Requests:
    def __init__(self, user_token, person_id, room_id):
        self.user_token = user_token
        self.person_id = person_id
        self.room_id = room_id
class StatusReq:
    def __init__(self, status,name,appointment,text,date,work_id):
        self.status = status
        self.name = name
        self.appointment = appointment
        self.text = text
        self.date = date
        self.work_id = work_id
#TODO remove this abomination 
class Button:
    def __init__(self, text, purpose):
        self.text = text
        self.purpose = purpose
        self.handler = None    
    def set_handler(self, handler):
        self.handler = handler    
    def handle(self, message):
        if self.handler is not None:
            self.handler(message)
        else:
            bot.send_message(message.chat.id, "На кнопку " + self.text + " не назначен обработчик" + rolling)

''' -------- globals ---------- '''
btn_All = []
main_menu_commands = dict(start = 'Начать работу с ботом', \
        user_manual = 'Получить инструкцию по использованию бота',\
        register = 'Зарегистрироваться', \
        dispatcher = 'Сообщить о проблеме диспетчеру', \
        check_status = 'Узнать статус заявки', \
        authorize = 'Авторизоваться', \
        rules = 'Получить правила проживания')

bot = telebot.TeleBot(API_KEY)

''' ============== common functions ============= '''
def get_houses():
    response = requests.get(base_url + 'api/houses/', auth=BearerAuth(token)).json()
    serd = orjson.dumps(response)
    data = orjson.loads(serd)["data"]
    address = []
    for record in data:
        address.append(House(record["address"]["street"], record["address"]["building"], record["house_id"]))
    return address
def btn_Disp():
    purpose = 'disp'
    buttons = []
    texts = ["Создать обращение здесь", "Позвонить диспетчеру"]
    for text in texts:
        buttons.append(Button(text,purpose))
    return buttons
def check_files(tg_id):
    wrk_dir = os.path.dirname(os.path.realpath(__file__)) + '/' + str(tg_id)
    if os.path.isdir(wrk_dir):
        if len(os.listdir(wrk_dir)) != 0:
            return True
        else:
            return False
def delete_files(tg_id):
    wrk_dir = os.path.dirname(os.path.realpath(__file__)) + '/' + str(tg_id)
    for filename in os.listdir(wrk_dir):
        file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print(f'Failed to delete {file_path}\nReason: {e}')
def list_pics(tg_id):
    files = []
    wrk_dir = os.path.dirname(os.path.realpath(__file__)) + '/' + str(tg_id)
    print(wrk_dir)
    for filename in os.listdir(wrk_dir):
        if os.path.splitext(filename)[1].lower() in ('.jpg', '.jpeg'):
            pic = wrk_dir + '/' + filename
            singlef = ('file', (filename , open(pic, 'rb'), 'image/jpeg' ))
            files.append(singlef)
    return files
def get_check_reg_old(house_id,room_number):
    print('house_id = ', house_id)
    print('room_number = ',room_number)
    response = requests.get(base_url + 'api2/user/check-reg-by-tg/?house_id=' + \
            str(house_id) + '&room_number=' + room_number, auth=BearerAuth(token)).json()
    serd = orjson.dumps(response)
    data = orjson.loads(serd)
    print(f'check-reg-by-tg returned\n', json.dumps(data, indent=4))
    return data["statusCode"]
def get_check_reg(house_id,room_number,account_number):
    print('house_id = ', house_id)
    print('room_number = ',room_number)
    print('account_number = ',account_number)

    response = requests.get(base_url + 'api2/user/check-reg-by-tg/?house_id=' + \
            str(house_id) + '&room_number=' + room_number + '&account_number=' + account_number, auth=BearerAuth(token)).json()
    serd = orjson.dumps(response)
    data = orjson.loads(serd)
    print(f'check-reg-by-tg returned\n', json.dumps(data, indent=4))
    return data["statusCode"]
def get_status(request_id):
    response = requests.get(base_url + 'api2/request/get-data-for-tg/?request_id=' + str(request_id), auth=BearerAuth(token)).json()
    serd = orjson.dumps(response)
    data = orjson.loads(serd)
    print(f'request_entry_tg returned\n', json.dumps(data, indent=4))
    if data["statusCode"] == 200:
        if isinstance(data.get('data'), list):
            print('Заявка в работе')
            depth = len(data["data"])
            item = data["data"][depth-1]
            name = item["first_name"] + ' ' + item["last_name"]
            return StatusReq(item["status"], name, item["appointment"], item["text"], item["date"], item["work_id"])
        elif isinstance(data.get('data'), dict):
            print('Заявка не обработана')
            return data["data"]["status"]
        else:
            print('ERROR wierd data in get-data-for-tg')
    else:
        return data["statusCode"]

def get_token(message, tg_id):
    response = requests.get(base_url + 'api2/user/get-token-by-tg-id/?tg_id=' + str(tg_id), auth=BearerAuth(token)).json()
    serd = orjson.dumps(response)
    data = orjson.loads(serd)
    print(f'get-token-by-tg-id response:\n',json.dumps(data,indent=4))
    if data["statusCode"] == 200:
        # yes, dispatcher request will be made with the FIRST room in array =:(
        req = Requests(data["data"]["token"], data["data"]["person_id"], data["data"]["room_ids"][0]) 
    else:
        req = data["statusCode"]
    return req #None
def do_inline_kbd(message,buttons,msg):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for key,value in buttons.items():
        item=types.InlineKeyboardButton(value, callback_data=key)
        markup.add(item)
    bot.send_message(message.chat.id, msg, reply_markup=markup)
def check_keywords(message):
    print(message.text[1:])
    for key,value in main_menu_commands.items():
        print('key:',key)
        if message.text[1:] == str(key):
            print('message.text[1:] == str(key)', str(key))
            if message.text[1:] == 'start':
                send_welcome(message)
#                reset_state(message)
            else:
                return True
    return False    
def reset_state(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    item = types.KeyboardButton(text="Removing of old kbd")
    markup.add(item)
    msg = bot.send_message(message.chat.id, "Убраем клавиатуру:", reply_markup=markup)
    fmesg = f'Вы отменили текущий процесс.\nЖду дальнейших команд{robot}'
    bot.send_message(message.chat.id,fmesg,reply_markup=types.ReplyKeyboardRemove())

### main menu constructor
def set_main_menu(message):
#    scope = telebot.types.BotCommandScopeDefault()
    scope = telebot.types.BotCommandScopeChat(message.chat.id)
    bot.delete_my_commands(scope=scope)
    cmds = []
    for key,value in main_menu_commands.items():
        cmd = types.BotCommand(command=str(key), description=value)
        cmds.append(cmd)
    bot.set_my_commands(cmds)

def set_handlers():
    for button in btn_All:
        if button.purpose == "disp":
            button.set_handler(handle_disp)
        elif button.purpose == "reg":
            button.set_handler(handle_reg)
        elif button.purpose == "phone":
            button.set_handler(handle_phone)
def handle_phone(message):
    markup = types.ForceReply(selective=False)

''' -------- bot commands decorators/handlers ---------- '''
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.set_chat_menu_button(message.chat.id, types.MenuButtonCommands('commands'))
    user_first_name = str(message.chat.first_name)
    user_last_name = str(message.chat.last_name)
    set_main_menu(message)
    fmesg = f'{user_first_name} {user_last_name},\nдобро пожаловать в чат-бот{robot}\n{UK_name}!'
    bot.send_message(message.chat.id,fmesg,reply_markup=types.ReplyKeyboardRemove())
    btns = dict(start_bot_help=open_book + " Получить инструкцию по использованию бота", start_bot_register=writing_hand + " Зарегистрироваться", \
            start_bot_dispatcher=shouting_head + " Сообщить о проблеме диспетчеру", start_bot_check_status=hourglass + " Узнать статус заявки" )
    do_inline_kbd(message, btns, 'Выберите действие кнопкой или командой меню:')

@bot.message_handler(commands=['rules'])
def send_rules(message):
    bot.send_message(message.chat.id, "Здесь будут правила проживания, когда их мне предоставят!")
@bot.message_handler(commands=['authorize'])
def main_authorize(message):
    auth_user(message)
@bot.message_handler(commands=['user_manual'])
def user_manual(message):
    fmesg = f'Здравствуйте! Это официальный бот {robot} Управляющей Компании {UK_name}.\n{green_check} Для начала работы выберите команду /start\n{green_check} Для использования бота необходимо зарегистрироваться или авторизоваться.\nЕсли Вам нужно зарегистрироваться, выберите нужный дом, а затем введите номер нужной квартиры. Затем отправьте номер своего телефона и придумайте пароль. В дальнейшем пароль пригодится для повторной авторизации(такое бывает{disappointed})\nЕсли у Вас уже есть аккаунт, авторизуйтесь командой /authorize, указав номер своего телефона и введите пароль.\n{green_check} Если у Вас возникла проблема, сообщите об этом диспетчеру с помощью команды /dispatcher.\nУ Вас есть возможность позвонить диспетчеру или оставить обращение здесь. Просто выберите одно из действий. Мы постараемся максимально оперативно решить Вашу проблему.\n{green_check} Также Вы можете узнать статус оставленной Вами заявки. Для это используйте команду /check_status\n{green_check} Чтобы получить эту инструкцию еще раз - используйте команду /user_manual\nБлагодарим Вас за использование нашего бота!'
    bot.send_message(message.chat.id, fmesg)
@bot.message_handler(commands=['check_status'])
def ask_request_id_for_status(message):
    markup = types.ForceReply(selective=False)
    fmesg = 'Пожалуйста укажите номер заявки.'
    bot.send_message(message.chat.id,fmesg,reply_markup=markup)
    bot.register_next_step_handler(message, check_status)

def check_status(message):
    text = message.text
    try:
        request_id = int(message.text)
        if request_id < 0 or request_id > max_req_num:
            bot.reply_to(message,f"Корректным номером заявки является число от 1 до {max_req_num}")
            ask_request_id_for_status(message)
            return None
    except ValueError:
        if check_keywords(message):
            bot.send_message(message.chat.id,'На этом этапе нашего общения нужно отправить мне номер заявки, а не команду.\nПопробуйте сделать запрос из главного меню еще раз!\n',reply_markup=types.ReplyKeyboardRemove())
            return None
        else:
            bot.reply_to(message, "Номер заявки - двузначное число без символов. Пожалуйста, введите число.")    
            ask_request_id_for_status(message)
            return None
    req = get_status(request_id)
    if isinstance(req,StatusReq):
        fmesg = f'{play}Статус заявки: {req.status}\nПоследнее изменение статуса:\n{blue_dia}Сотрудник: {req.name}\n{blue_dia}Дата: {req.date}\n{blue_dia}Комментарий: {req.text}'
        bot.send_message(message.chat.id,fmesg,reply_markup=types.ReplyKeyboardRemove())
    elif isinstance(req,str):
        bot.send_message(message.chat.id,f'{pause}Статус заявки: {req}',reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id,f'Такого номера заявки не существует{rolling}',reply_markup=types.ReplyKeyboardRemove())
    
@bot.message_handler(commands=['dispatcher'])
def dispatcher_inquiry(message):   
    buttons = btn_Disp()
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button in buttons:
        item = types.KeyboardButton(button.text)
        markup.add(item)
        btn_All.append(button)
    bot.send_message(message.chat.id,'Пожалуйста, сделайте выбор',reply_markup=markup)
@bot.message_handler(commands=['register'])
def register_user(message):
    purpose = "reg"
    global houses2reg
    houses2reg = []
    houses2reg.clear()
    houses2reg = get_houses()
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for house in houses2reg:
        btn_text = str(house.street + ' ' + house.bld)
        btn_All.append(Button(btn_text,purpose))
        item=types.KeyboardButton(btn_text)
        markup.add(item)
    bot.send_message(message.chat.id,'Пожалуйста, выберите Ваш дом',reply_markup=markup)
''' ------------ handler by content_types ------------ '''
@bot.message_handler(content_types='text')
def text_handler(message):
    button_text = message.text
    set_handlers()
    for button in btn_All:
        if button_text == button.text:
            button.handle(message)
            break
#TODO HERE to add a routine for basic communication with the bot

@bot.message_handler(content_types='photo')
def photo_menu(message):
    print('This message got an image!')
    buttons = ("Создать заявку с этим фото","Добавить к созданной заявке","Сохранить для дальнейшего использования")
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    print('file.file_path =', file_info.file_path)
#    file_url = f'https://api.telegram.org/file/bot{API_KEY}/{file_info.file_path}'
    file_url = tgdload_url + file_info.file_path
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for button in buttons:
        item=types.KeyboardButton(button)
        markup.add(item)
    bot.send_message(message.chat.id,'Вы отправили мне фото. Что с ним сделать?',reply_markup=markup)
    bot.register_next_step_handler(message, photo_handler, file_url)

def photo_handler(message, file_url):
    button_text = message.text
    tg_id = message.from_user.id
    if button_text == 'Создать заявку с этим фото':
        send_req(message,tg_id,file_url)
    elif button_text == 'Добавить к созданной заявке':
        update_req(message, file_url)
    elif button_text == 'Сохранить для дальнейшего использования':
        save_file_to_disk(message, file_url)
    else:
        bot.send_message(message.chat.id,'Фото удалено' + expressionless)

def save_file_to_disk(message, file_url):
    print('file_url is', file_url)
    if file_url is None:
        if message.content_type == 'photo':
            fileID = message.photo[-1].file_id
            print('fileID =', fileID)
            file_info = bot.get_file(fileID)
            print('file.file_path =', file_info.file_path)
            file_url = tgdload_url + file_info.file_path
        else:
            print('ERROR message.content_type is not PHOTO')
    else:
        print('file_url is', file_url)
    file_info_file_path = file_url[len(tgdload_url):]
    print('extracted file_info_file_path',file_info_file_path)
    file_desc = bot.download_file(file_info_file_path)
    tg_id = str(message.from_user.id)
    wrk_dir = os.path.dirname(os.path.realpath(__file__)) + '/' + tg_id
    if not os.path.isdir(wrk_dir):
        os.mkdir(wrk_dir)
    filename = 'image' + str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S")) + '.jpg'
    full_path = wrk_dir + '/' + filename 
    print('filename:',filename)
    print('full_path',full_path)
    with open(full_path, 'wb') as new_file:
        new_file.write(file_desc)
    bot.send_message(message.chat.id, 'Файл принят')
    #inline keyboard

''' ------------ InlineKeyboard handler ------------ '''

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            if call.data == 'start_bot_help':
                user_manual(call.message)
            if call.data == 'start_bot_register':
                register_user(call.message)
            if call.data == 'start_bot_dispatcher':
                dispatcher_inquiry(call.message)
            if call.data == 'start_bot_check_status':
                ask_request_id_for_status(call.message)
            if call.data == 'chg_house':
                register_user(call.message)
            if call.data == 'chg_room':
                markup = types.ForceReply(selective=False)
                msg = bot.send_message(message.chat.id,'Пожалуйста, введите номер квартиры',reply_markup=markup)
                bot.register_next_step_handler(msg, handle_room_number, street, bld, house_id)
            if call.data == 'chg_phone':
                fmesg = f'В данный момент ручной ввод и/или корректировка номера телефона не поддерживается...\
                        {upset}\nДля логина можно использовать только тот номер телефона, который привязан к \
                        Телеграм.\nСпасибо за понимание!'
                bot.send_message(call.message.chat.id, fmesg)
            if call.data == 'reg_user':
                register_user(call.message)
            if call.data == 'auth_user':
                auth_user(call.message)
            if call.data == 'auth_send_req':
                send_req(call.message,call.from_user.id,None)
            if call.data == 'auth_do_nothing':
                bot.send_message(call.message.chat.id,'Ок, ничего - так ничего' + expressionless,reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        print(repr(e))
''' -------- bot commands decorators/handlers end ---------- '''


''' ------------ register begin ------------ '''
def handle_reg(message):
    street = message.text.split()[0]
    bld = message.text.split()[1] 
    for house in houses2reg:
        if house.street == street and house.bld == bld:
            house_id = house.house_id
    markup = types.ForceReply(selective=False)
    msg = bot.send_message(message.chat.id,'Пожалуйста, введите номер квартиры',reply_markup=markup)
    bot.register_next_step_handler(msg, handle_room_number, street, bld, house_id)
def handle_room_number(message, street, bld, house_id):
    if not message.text.isdigit():
        bot.send_message(message.chat.id,'Пока я умею работать только с номерами квартир, \
                состоящими из цифр. Пожалуйста укажите номер квартиры заново')
        handle_reg(message)
        return None
    else:
        room_number = str(message.text)
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id,f'Пожалуйста, введите номер лицевого счёта.\nЕго Вы можете получить по телефону {UK_phone}',reply_markup=markup)
        bot.register_next_step_handler(msg, handle_account_number, street, bld, house_id, room_number)

def handle_account_number(message, street, bld, house_id, room_number):
    if not message.text.isdigit():
        bot.send_message(message.chat.id,'Пока я умею работать только с номерами лицевых счетов, \
                состоящими из цифр. Пожалуйста укажите номерами лицевого счета заново')
        handle_reg(message)
        return None
    else:
        account_number = str(message.text)
        result = get_check_reg(house_id, room_number, account_number)
        if result == 200:
            ask_phone_number(message, street, bld, house_id, room_number, account_number)
        elif result == 410:        
            bot.send_message(message.chat.id,'Дом не найден ' + robot)
        elif result == 420:        
            bot.send_message(message.chat.id,'Квартира не найдена ' + robot)
        elif result == 430:        
            bot.send_message(message.chat.id,'Номер лицевого счета указан неверно ' + robot)
        elif result == 400:
            bot.send_message(message.chat.id,'По этому адресу уже зарегистрирован пользователь ' + rolling)
            # add option to re-register
            btns = dict(reg_user="Зарегистрироваться по другому адресу", auth_user="Авторизоваться")
            do_inline_kbd(message, btns,'Выберите дальнейшие действия')

def ask_phone_number(message, street, bld, house_id, room_number, account_number):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    item = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    markup.add(item)
    msg = bot.send_message(message.chat.id, "Пожалуйста, отправьте свой номер телефона:", reply_markup=markup)
    bot.register_next_step_handler(msg, ask_password, street, bld, house_id, room_number, account_number)


def ask_password(message, street, bld, house_id, room_number, account_number):
    if message.contact is not None:
        phone_number = message.contact.phone_number
        bot.send_message(message.chat.id, "Пожалуйста, придумайте пароль, который будет использоваться в дальнейшем для авторизации и введите его здесь:")
        bot.register_next_step_handler(message, check_password, street, bld, house_id, room_number, account_number, phone_number)
    elif check_keywords(message):
        msg = bot.send_message(message.chat.id,'На этом этапе нашего общения нужно отправить мне Ваш контакт посредством нажатия кнопки, а не команду меню.\n',reply_markup=types.replyKeyboardHide())
        ask_phone_number(message, street, bld, house_id, room_number, account_number)
        return None
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте свой номер телефона с помощью кнопки.",reply_markup=types.ReplyKeyboardRemove())
        ask_phone_number(message,street, bld, house_id, room_number, account_number)
        return None
def check_password(message, street, bld, house_id, room_number, account_number, phone_number):
    password = message.text
    bot.delete_message(message.chat.id, message.id)
    bot.send_message(message.chat.id, "Пожалуйста, повторно введите пароль:")
    bot.register_next_step_handler(message, post_reg_by_tg, street, bld, house_id, room_number, account_number, phone_number, password)
def post_reg_by_tg(message, street, bld, house_id, room_number, account_number, phone_number, password):
    confirm_password = message.text
    #TODO add deleteMessage method
    if confirm_password == password:
        tg_id = str(message.from_user.id)
        response = f"Ваши данные для входа в систему:\nлогин: {phone_number}\nпароль: {password}"
        bot.send_message(message.chat.id, response)
        jsdict = {"login": phone_number[1:], "password": password, "room_number": room_number, "account_number": account_number, "house_id": house_id, "tg_id": tg_id}
        serd = orjson.dumps(jsdict)
        data = orjson.loads(serd)
        print(json.dumps(data,indent=4))
        response = requests.post(base_url + 'api2/user/register-by-tg/', auth=BearerAuth(token), headers=post_headers, json=data).json()
        serd = orjson.dumps(response)
        data = orjson.loads(serd)
        if data["statusCode"] == 200:
            fmesg = f'Поздравляем!{celebrate}\nВы зарагистрированы в системе!\nТеперь Вам доступны все сервисы'
            bot.send_message(message.chat.id, fmesg)
        else:
            bot.send_message(message.chat.id,data["data"]["error"])
    else:
        bot.send_message(message.chat.id, "Пароли не совпадают. Пожалуйста, введите пароль заново:")
        bot.register_next_step_handler(message, check_password, street, bld, house_id, room_number, account_number, phone_number)
''' ------------ register end ------------ '''
''' ------------ auth begin ------------ '''
def auth_user(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    item = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    markup.add(item)
    bot.send_message(message.chat.id, "Пожалуйста, отправьте свой номер телефона:", reply_markup=markup)
    bot.register_next_step_handler(message, ask_password_auth)

def ask_password_auth(message):
    if check_keywords(message):
        bot.send_message(message.chat.id, "Если Вы передумали, отправьте команду /start из главного меню.\
                Другие команды сейчас не работают" + expressionless)
    if message.contact is not None:
        phone_number = message.contact.phone_number
        bot.send_message(message.chat.id, "Пожалуйста, введите пароль:")
        bot.register_next_step_handler(message, auth_tg_user, phone_number)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте свой номер телефона с помощью кнопки.\
                Если Вы передумали, отправьте команду /start из главного меню" + hug,reply_markup=types.ReplyKeyboardRemove())
        auth_user(message)

def auth_tg_user(message, phone_number):
    password = message.text
    jsdict = {"login": phone_number[1:], "password": password}
    serd = orjson.dumps(jsdict)
    data = orjson.loads(serd)
#   print(json.dumps(data,indent=4))
    response = requests.post(base_url + 'api2/user/auth-tg/', auth=BearerAuth(token), headers=post_headers, json=data).json()
    serd = orjson.dumps(response)
    data = orjson.loads(serd)
    if data["statusCode"] == 200:
        
        bot.send_message(message.chat.id,'Успешная авторизация')
        print('tg_id@Inlinekbd',message.from_user.id)
        btns = dict(auth_send_req="Создать запрос в диспетчерскую", auth_do_nothing="Ничего не делать" )
        do_inline_kbd(message, btns,'Далее могу предложить')
    else:
        bot.send_message(message.chat.id,data["data"]["error"])
        #ask whether user want to continue or want to stop
        auth_user(message)

''' ------------ auth end ------------ '''
''' ------------ dispatcher begin ------------ '''
def handle_disp(message):
    button_text = message.text
    if button_text == "Создать обращение здесь":
        send_req(message,message.from_user.id,None)
        #use check auth by 
    elif button_text == "Позвонить диспетчеру":
        bot.send_message(message.chat.id,f'Телефон диспетчерской {UK_phone}')
    else:
        bot.send_message(message.chat.id,'нужно выбрать из 2 вариантов')
        handle_disp(message)

def send_req(message,tg_id,file_url):
    print('send_req for tg_id:',tg_id)
    req = get_token(message, tg_id)
    if isinstance(req,Requests):
        print('user_token = ',req.user_token)
        markup = types.ForceReply(selective=False)
        fmesg = f'Кратко, в ОДНОМ сообщении, изложите суть проблемы.\nДиспетчер ответит Вам при первой возможности.'
        bot.send_message(message.chat.id,fmesg,reply_markup=markup)
        print('text right before bot.register_next_step_handler ',message.text)
        bot.register_next_step_handler(message, post_disp_user, req, file_url)
    elif isinstance(req,int):
        if req == 400:
            bot.send_message(message.chat.id,'Необходимо авторизоваться')
            auth_user(message)
        elif req == 410:
            bot.send_message(message.chat.id,'Необходимо зарегистрироваться')
            register_user(message)   
        else:
            print('ERROR! Unexpected statusCode ',req)
    else:
        print('get_token returned garbage',req)
def post_disp_user(message, req, file_url):
    tg_id = message.from_user.id
    print('text right before check_keywords ',message.text)
    fileID = None
    if message.content_type == 'photo':
        text = message.caption
        if text is None:
            bot.send_message(message.chat.id,f'Простите, но просто фото, без текста, я принять не могу.\nПовторите запрос, добавив описание к этому фото.\n',reply_markup=types.ReplyKeyboardRemove())
            return None
        fileID = message.photo[-1].file_id
        print('fileID =', fileID)
    elif message.content_type == 'text':
        text = message.text
        if check_keywords(message):
            bot.send_message(message.chat.id,'На этом этапе нашего общения нужно отправить мне текст заявки, а не команду.\nПопробуйте еще раз!\n',reply_markup=types.ReplyKeyboardRemove())
            return None
    else:
        bot.send_message(message.chat.id,f'Пока я не умею обращаться с таким типом входных данных.\nДавайте попробуем еще раз!\nТолько в этот раз отправьте мне текст и/или фото')
        send_req(message,tg_id,file_url)
    jsdict = dict(subject="Запрос из телеграм-бота", text=text, source_type=5, room_id=req.room_id, person_id=req.person_id)
    serd = orjson.dumps(jsdict)
    data = orjson.loads(serd)
    print(f'post_disp_user request json\n',json.dumps(data,indent=4))
    response = requests.post(base_url + 'api/requests/', auth=BearerAuth(req.user_token), headers=post_headers, json=data).json()
    serd = orjson.dumps(response)
    data = orjson.loads(serd)
    print(f'post_disp_user response json\n',json.dumps(data,indent=4))
    if data["statusCode"] == 200:
        request_id = data["data"]["request_id"]
        bot.send_message(message.chat.id,"Ваша заявка принята, номер заявки: " + str(request_id))
        bot.send_message(message.chat.id,"Спасибо за обращение!" + hug)
        print('fileID=',fileID)
        if fileID is not None or file_url is not None:
            bot.send_message(message.chat.id,"Отправляю приложенное к заявке фото " + robot)
            post_pics_to_req(message, req, request_id, file_url)
    elif data["statusCode"] == 410:
        print('ERROR: \'Text\' field was sent as empty')
    else:
        print(data["data"]["error"])
''' ------------ dispatcher end ------------ '''
''' ------------ pictures begin ------------ '''
def check_req_num(message, req, request_id, file_url):
    max_req_num = 99
    tg_id = message.from_user.id
    if request_id is None:
        try:
            request_id = int(message.text)
            if request_id < 0 or request_id > max_req_num:
                bot.reply_to(message, "Пожалуйста, введите корректный номер заявки")
                update_req(message, file_url)
        except ValueError:
            bot.reply_to(message, "Номер заявки - двузначное число без символов. Пожалуйста, введите число.")
            update_req(message, file_url)
    post_pics_to_req(message, req, request_id, file_url)
def update_req(message, file_url):
    tg_id = message.from_user.id
    req = get_token(message, tg_id)
    markup = types.ForceReply(selective=False)
    fmesg = f'Введите номер заявки, к которой хотите приложить фото\n(если забыли - посмотрите в истории нашего общения).'
    msg = bot.send_message(message.chat.id,fmesg,reply_markup=markup)
    bot.register_next_step_handler(msg, check_req_num, req, None, file_url)
def post_pics_to_req(message, req, request_id, file_url):
    tg_id = message.from_user.id
    if file_url is None:
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        file_url = f'https://api.telegram.org/file/bot{API_KEY}/{file_info.file_path}'
    r = requests.get(file_url, stream=True)
    if r.status_code == 200:
        img_req = r.content
        files= {'file': ('image.jpg', img_req, 'image/jpeg')}
        response = requests.post(base_url + 'api/uploads/requests/' + str(request_id) + '/', auth=BearerAuth(req.user_token), files=files, verify=False).json()
        serd = orjson.dumps(response)
        data = orjson.loads(serd)
        print(f'api/uploads/requests/ response json\n',json.dumps(data,indent=4))
        if data["statusCode"] == 200:
            bot.send_message(message.chat.id,'Файл по заявке ' + str(request_id) +' успешно отправлен!')
        elif data["statusCode"] == 400:
            bot.send_message(message.chat.id,'Для отправки файлов необходимо авторизоваться')
        else:
            bot.send_message(message.chat.id, data["data"]["error"])
    else:
        print('ERROR Cannot get a file from TG. Plain text mb?')
''' ------------ pictures end ------------ '''


''' ============== main() ============= '''
print('bot started')
bot.infinity_polling()

