# -*- coding: utf-8 -*-

import logging

import telegram
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import CallbackContext, CommandHandler
from telegram import ParseMode, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, ParseMode

from game import Game
import settings

puan_dict = {}

logger = None

games = {}


def get_or_create_game(chat_id: int) -> Game:
    global games
    game = games.get(chat_id, None)
    if game is None:
        game = Game()
        games[chat_id] = game

    return game


def setup_logger():
    global logger
    file_handler = logging.FileHandler('husnu.log', 'w', 'utf-8')
    stream_handler = logging.StreamHandler()
    logger = logging.getLogger("main_log")
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def yardim(update, context):
    update.message.reply_text('📃Kurallar çok basit, Bot size bir rakam gösterecek ve bu rakamı gruptaki kullanıcılara bir hesaplama şeklinde söylemelisiniz🪁\n\nÖrnek: Bot size 5 sayısını gösterdi ve siz 3+2=? böyle bir sorudan bahsetmelisin🤹‍♂️\n🛑 Bot yalnız gruplar için tasarlanmışdır\n\n' +
                              'Mevcut Komutlar⬇️\n' +
                              '/oyun - Yeni oyun başlatmak🎯\n' +
                              '/ogretmen - Öğretmen olmak🗣\n' +
                              '/puan - Grup üzre puanlar📈', reply_to_message_id=True)


def button(update, context):
    user_id = update.callback_query.from_user.id
    chat_id = update.callback_query.message.chat_id
    bot = telegram.Bot(token=settings.TOKEN)

    game = get_or_create_game(chat_id)

    query = update.callback_query

    if query.data == 'show_word':
        word = game.get_word(user_id)
        if game.is_ogretmen(query.from_user.id):
            bot.answer_callback_query(callback_query_id=query.id, text=word, show_alert=True)

    if query.data == 'change_word':
        word = game.change_word(user_id)
        if game.is_ogretmen(query.from_user.id):
            bot.answer_callback_query(callback_query_id=query.id, text=word, show_alert=True)


def command_start(update, context: CallbackContext):
    if update.effective_chat.type == "private":
        
        addme = InlineKeyboardButton(text="✅ Botu Grupa Ekle", url="https://t.me/botnamebot?startgroup=a")
        admin = InlineKeyboardButton(text="Bot Fikri @HusnuEhedov", url="t.me/husnuehedov")

        keyboard = [[addme],[admin]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('🙋🏻‍♂️🎉 Hesab Oyun Botuna Hoşgeldiniz\n\nBot hakkında ve tüm komutları görmek için\n/yardim komutunu yazmak yeterlidir⚡️', reply_to_message_id=True, reply_markup=reply_markup)
    else:
        chat_id = update.message.chat.id
        user_id = update.message.from_user.id
        username = update.message.from_user.full_name

        logger.info('Got command /oyun,'
                    'chat_id={},'
                    'user_id'.format(chat_id,
                                     user_id))

        game = get_or_create_game(chat_id)
        game.start()

        update.message.reply_text('👩🏻‍🏫Hesab oyunu başladı\nMatematiğine güveniyorsun❔\nHadi Oynayalım🎯'.format(username), reply_to_message_id=True)

        set_ogretmen(update, context)


def set_ogretmen(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    username = update.message.from_user.full_name
    logger.info('chat_id={}, New master is "{}"({})'.format(chat_id,
                                                            username,
                                                            update.message.from_user.id))

    game = get_or_create_game(chat_id)

    game.set_ogretmen(update.message.from_user.id)

    show_word_btn = InlineKeyboardButton("🔍🔢Rakama Bak", callback_data='show_word')
    

    keyboard = [[show_word_btn]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('[{}](tg://user?id={}) _Şimdi sizlere bir soru gösterecek, grup kullanıcıları dikkatli olun ve hızlı hesaplayın_ 🎭🎲'.format(username,user_id), reply_to_message_id=True, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


def command_ogretmen(update: Update, context):
    chat_id = update.message.chat.id
    game = get_or_create_game(chat_id)
    username = update.message.from_user.full_name
    user_id = update.message.from_user.id

    if not game.is_game_started():
        return

    if not game.is_ogretmen_time_left():
        update.message.reply_text('Öğretmen olmak için {} saniye var⛔️\n\nResmi Kanal - @repohane 📣'.format(game.get_ogretmen_time_left()),
                                  reply_to_message_id=True)
        return

    logger.info('Got command /ogretmen,'
                'chat_id={},'
                'user="{}"({}),'
                'timedelta={}'.format(chat_id,
                                      username,
                                      user_id,
                                      game.get_ogretmen_time_left()))

    set_ogretmen(update, context)


def command_show_word(update, context):
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id

    game = get_or_create_game(chat_id)
    word = game.get_word(user_id)

    logger.info('Got command /show_word, ' 
                'chat_id={}, '
                'user="{}"({}),'
                'is_user_ogretmen={},'
                'word={}'.format(chat_id,
                                 update.message.from_user.full_name,
                                 update.message.from_user.id,
                                 game.is_ogretmen(user_id),
                                 word))

    update.message.reply_text(word, reply_to_message_id=True)


def command_change_word(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id

    game = get_or_create_game(chat_id)

    word = game.change_word(user_id)

    logger.info('Got command /change_word,'
                'chat_id={},'
                'user="{}"({}),'
                'is_user_ogretmen={},'
                'word={}'.format(chat_id,
                                 update.message.from_user.full_name,
                                 user_id,
                                 game.is_ogretmen(user_id),
                                 word))

    update.message.reply_text(word, reply_to_message_id=True)


def command_puan(update, context):
    chat_id = update.message.chat.id

    game = get_or_create_game(chat_id)

    puan_str = game.get_str_puan()

    logger.info('Got command /puan,'
                'chat_id={},'
                'puan={}'.format(update.message.chat.id,
                                   puan_str))

    update.message.reply_text(puan_str, reply_to_message_id=True)


def is_word_answered(update, context):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    username = update.message.from_user.full_name
    text = update.message.text

    game = get_or_create_game(chat_id)

    word = game.get_current_word()

    if game.is_word_answered(user_id, text):
        update.message.reply_text('*{}* _rakamını_ [{}](tg://user?id={}) _buldu_📌_Artık o yeni Öğretmen_👩🏼‍🏫'.format(word, username,user_id), reply_to_message_id=True, parse_mode=ParseMode.MARKDOWN)

        game.update_puan(user_id, username)

        set_ogretmen(update, context)

    logger.info('Guessing word,'
                'chad_id={},'
                'user="{}"({}),'
                'is_ogretmen={},'
                'text="{}",'
                'word="{}"'.format(update.message.chat.id,
                                   update.message.from_user.full_name,
                                   update.message.from_user.id,
                                   game.is_ogretmen(user_id),
                                   text,
                                   word))


def main():
    setup_logger()

    updater = Updater(settings.TOKEN, use_context=True)

    bot = updater.bot

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("oyun", command_start))
    dp.add_handler(CommandHandler("ogretmen", command_ogretmen))
    dp.add_handler(CommandHandler("show_word", command_show_word))
    dp.add_handler(CommandHandler("change_word", command_change_word))
    dp.add_handler(CommandHandler("puan", command_puan))
    dp.add_handler(CommandHandler("yardim", yardim))
    dp.add_handler(CommandHandler("start", command_start))

    dp.add_handler(CallbackQueryHandler(button))

    dp.add_handler(MessageHandler(Filters.text, is_word_answered))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
