from ._bot import bot, BOT_TOKEN
from telebot import types
from ._filters_enum import Filters
import improc as im


# dict with photoes by chat
chat_dict = {}


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


@bot.message_handler(content_types=['photo'])
def send_selection_filter_keybord(message):
    photo_path_mask = 'https://api.telegram.org/file/bot{token}/{file_path}'

    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    photo_path = photo_path_mask.format(token=BOT_TOKEN,
                                        file_path=file_info.file_path)

    chat_id = message.chat.id
    chat_dict[chat_id] = photo_path

    markup = types.ReplyKeyboardMarkup()

    for filt in Filters:
        filt_name = filt.name.replace('_', ' ')
        filt_button = types.KeyboardButton(filt_name)
        markup.add(filt_button)

    msg = bot.reply_to(message, "Choose one filter:", reply_markup=markup)
    bot.register_next_step_handler(msg, apply_filter)


def apply_filter(message):
    chat_id = message.chat.id
    photo_path = chat_dict[chat_id]
    photo = im.io.imread(photo_path)

    filt_name = message.text.replace(' ', '_')
    if filt_name == Filters.Gaussian_filter.name:
        photo = im.gaussian_filter(photo)
    elif filt_name == Filters.Gray_filter.name:
        photo = im.rgb2gray(photo)
    elif filt_name == Filters.Edge_filter.name:
        photo = im.detect_edge(photo)
    elif filt_name == Filters.Adjust_contrast_brightness.name:
        photo = im.adjust_contast_brightness(photo, 0.5, 0.5)
    else:
        bot.reply_to(message, "Oooups")
        return

    photo = im.img_as_ubyte(photo)
    im.io.imsave('photo_{chat_id}.jpg'.format(chat_id=chat_id), photo)

    img = open('photo_{chat_id}.jpg'.format(chat_id=chat_id), 'rb')
    bot.send_photo(chat_id, img, reply_to_message_id=message.message_id)
    img.close()
