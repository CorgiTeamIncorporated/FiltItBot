from ._bot import bot, BOT_TOKEN
from telebot import types
from ._filters_enum import Filters
import improc as im


# dict with photos by message
chat_dict = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! To start using the bot, send him a photo")


@bot.message_handler(commands=['help'])
def send_doc(message):
    gaus = "Gaussian filter - apply blur, kernel size = [0, 32, 1]"
    gray = "Grayscale filter - apply grayscale filter"
    edge = "Edge filter - finding edges on a photo, threshold = [0, 1, 0.1]"
    cb = "Adjust contrast brightness - contrast = [-1, 3, 0.1], brightness = [-1, 3, 0.1]"
    bot.reply_to(message, gaus + "\n" + gray + "\n" + edge + "\n" + cb)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Sorry, but I don't speak to strangers")


@bot.message_handler(content_types=['photo'])
def send_selection_filter_keybord(message):
    chat_id = message.chat.id
    if chat_id in chat_dict:
        bot.reply_to(message, 'Apply previous photo changes')
        return

    photo_path_mask = 'https://api.telegram.org/file/bot{token}/{file_path}'

    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    photo_path = photo_path_mask.format(token=BOT_TOKEN,
                                        file_path=file_info.file_path)
    chat_dict[chat_id] = {"photo_path": photo_path}

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    for filt in Filters:
        filt_name = filt.name.replace('_', ' ')
        filt_button = types.KeyboardButton(filt_name)
        markup.add(filt_button)

    msg = bot.reply_to(message, "Choose one filter:", reply_markup=markup)
    bot.register_next_step_handler(msg, apply_filter)


def apply_filter(message):
    filt_name = message.text.replace(' ', '_')
    if filt_name == Filters.Gaussian_filter.name:
        apply_gaussian_filter(message)
    elif filt_name == Filters.Gray_filter.name:
        apply_gray_filter(message)
    elif filt_name == Filters.Edge_filter.name:
        apply_edge_filter(message)
    elif filt_name == Filters.Adjust_contrast_brightness.name:
        adjust_contast_brightness(message)
    else:
        bot.reply_to(message, "Oooups")
        return


def apply_gaussian_filter(message, kernel_size=3, is_first=True):
    chat_id = message.chat.id

    photo_path = chat_dict[chat_id]["photo_path"]
    photo = im.io.imread(photo_path)
    photo = im.gaussian_filter(photo, kernel_size)
    im.io.imsave('photo_{chat_id}.jpg'.format(chat_id=chat_id), photo)

    keyboard = types.InlineKeyboardMarkup()
    logo_kernel = types.InlineKeyboardButton(text="Kernel size",
                                             callback_data="is_cap")

    dec_kernel = types.InlineKeyboardButton(text="<",
                                            callback_data="gaussian_dec")
    logo_kernel_size = types.InlineKeyboardButton(text=kernel_size,
                                                  callback_data="is_cap")
    adj_kernel = types.InlineKeyboardButton(text=">",
                                            callback_data="gaussian_adj")
    apply = types.InlineKeyboardButton(text="apply",
                                       callback_data="apply")

    keyboard.add(logo_kernel)
    keyboard.row(dec_kernel, logo_kernel_size, adj_kernel)
    keyboard.add(apply)

    img = open('photo_{chat_id}.jpg'.format(chat_id=chat_id), 'rb')

    if is_first:
        bot.send_photo(chat_id, img, reply_markup=keyboard,
                       reply_to_message_id=message.message_id)
    else:
        bot.edit_message_media(types.InputMedia(type='photo', media=img),
                               chat_id=chat_id,
                               reply_markup=keyboard,
                               message_id=message.message_id)
    img.close()
    chat_dict[chat_id]["gaussian_kernel"] = kernel_size
    chat_dict[chat_id]["is_in_process"] = False


def apply_gray_filter(message):
    chat_id = message.chat.id

    photo_path = chat_dict[chat_id]["photo_path"]
    photo = im.io.imread(photo_path)
    photo = im.rgb2gray(photo)
    im.io.imsave('photo_{chat_id}.jpg'.format(chat_id=chat_id), photo)

    img = open('photo_{chat_id}.jpg'.format(chat_id=chat_id), 'rb')
    bot.send_photo(chat_id, img,
                   reply_to_message_id=message.message_id)
    img.close()
    del chat_dict[chat_id]


def apply_edge_filter(message, threshhold=0.5, is_first=True):
    chat_id = message.chat.id

    photo_path = chat_dict[chat_id]["photo_path"]
    photo = im.io.imread(photo_path)
    photo = im.detect_edge(photo, threshhold)
    im.io.imsave('photo_{chat_id}.jpg'.format(chat_id=chat_id), photo)

    keyboard = types.InlineKeyboardMarkup()
    logo_threshold = types.InlineKeyboardButton(text="Threshhold",
                                                callback_data="is_cap")

    dec_threshold = types.InlineKeyboardButton(text="<",
                                               callback_data="edge_dec")
    logo_threshold_size = types.InlineKeyboardButton(text=round(threshhold, 1),
                                                     callback_data="is_cap")
    adj_threshold = types.InlineKeyboardButton(text=">",
                                               callback_data="edge_adj")
    apply = types.InlineKeyboardButton(text="apply",
                                       callback_data="apply")

    keyboard.add(logo_threshold)
    keyboard.row(dec_threshold, logo_threshold_size, adj_threshold)
    keyboard.add(apply)

    img = open('photo_{chat_id}.jpg'.format(chat_id=chat_id), 'rb')

    if is_first:
        bot.send_photo(chat_id, img, reply_markup=keyboard,
                       reply_to_message_id=message.message_id)
    else:
        bot.edit_message_media(types.InputMedia(type='photo', media=img),
                               chat_id=chat_id,
                               reply_markup=keyboard,
                               message_id=message.message_id)
    img.close()
    chat_dict[chat_id]["edge_threshold"] = threshhold
    chat_dict[chat_id]["is_in_process"] = False


def adjust_contast_brightness(message, contrast=1.0, brightness=0.0,
                              is_first=True):
    chat_id = message.chat.id

    photo_path = chat_dict[chat_id]["photo_path"]
    photo = im.io.imread(photo_path)
    photo = im.adjust_contast_brightness(photo, contrast, brightness)
    im.io.imsave('photo_{chat_id}.jpg'.format(chat_id=chat_id), photo)

    keyboard = types.InlineKeyboardMarkup()
    logo_contrast = types.InlineKeyboardButton(text="Contrast",
                                               callback_data="is_cap")

    dec_contrast = types.InlineKeyboardButton(text="<",
                                              callback_data="contrast_dec")
    logo_contrast_size = types.InlineKeyboardButton(text=round(contrast, 1),
                                                    callback_data="is_cap")
    adj_contrast = types.InlineKeyboardButton(text=">",
                                              callback_data="contrast_adj")

    logo_bright = types.InlineKeyboardButton(text="Brightness",
                                             callback_data="is_cap")
    dec_bright = types.InlineKeyboardButton(text="<",
                                            callback_data="bright_dec")
    logo_bright_size = types.InlineKeyboardButton(text=round(brightness, 1),
                                                  callback_data="is_cap")
    adj_bright = types.InlineKeyboardButton(text=">",
                                            callback_data="bright_adj")

    apply = types.InlineKeyboardButton(text="apply",
                                       callback_data="apply")

    keyboard.add(logo_contrast)
    keyboard.row(dec_contrast, logo_contrast_size, adj_contrast)
    keyboard.add(logo_bright)
    keyboard.row(dec_bright, logo_bright_size, adj_bright)
    keyboard.add(apply)

    img = open('photo_{chat_id}.jpg'.format(chat_id=chat_id), 'rb')

    if is_first:
        bot.send_photo(chat_id, img, reply_markup=keyboard,
                       reply_to_message_id=message.message_id)
    else:
        bot.edit_message_media(types.InputMedia(type='photo', media=img),
                               chat_id=chat_id,
                               reply_markup=keyboard,
                               message_id=message.message_id)
    img.close()
    chat_dict[chat_id]["contrast"] = contrast
    chat_dict[chat_id]["brightness"] = brightness
    chat_dict[chat_id]["is_in_process"] = False


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    is_in_process = chat_dict[chat_id]["is_in_process"]
    if is_in_process:
        bot.reply_to(call.message, "Image processing, please wait...")
        return
    else:
        chat_dict[chat_id]["is_in_process"] = True

    if call.data == "is_cap":
        pass

    elif call.data == "apply":
        bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=None)
        del chat_dict[chat_id]
        return

    elif call.data == "gaussian_dec":
        kernel_size = chat_dict[chat_id]["gaussian_kernel"]
        if kernel_size < 2:
            chat_dict[chat_id]["is_in_process"] = False
            return

        kernel_size -= 1
        apply_gaussian_filter(call.message, kernel_size, is_first=False)

    elif call.data == "gaussian_adj":
        kernel_size = chat_dict[chat_id]["gaussian_kernel"]
        if kernel_size > 31:
            chat_dict[chat_id]["is_in_process"] = False
            return

        kernel_size += 1
        apply_gaussian_filter(call.message, kernel_size, is_first=False)

    elif call.data == "edge_dec":
        threshhold = chat_dict[chat_id]["edge_threshold"]
        if threshhold < 0.1:
            chat_dict[chat_id]["is_in_process"] = False
            return

        threshhold -= 0.1
        apply_edge_filter(call.message, threshhold, is_first=False)

    elif call.data == "edge_adj":
        threshhold = chat_dict[chat_id]["edge_threshold"]
        if threshhold > 0.9:
            chat_dict[chat_id]["is_in_process"] = False
            return

        threshhold += 0.1
        apply_edge_filter(call.message, threshhold, is_first=False)

    elif call.data == "contrast_dec":
        brightness = chat_dict[chat_id]["brightness"]
        contrast = chat_dict[chat_id]["contrast"]
        if contrast < 0.1:
            chat_dict[chat_id]["is_in_process"] = False
            return

        contrast -= 0.1
        adjust_contast_brightness(call.message, contrast, brightness,
                                  is_first=False)

    elif call.data == "contrast_adj":
        brightness = chat_dict[chat_id]["brightness"]
        contrast = chat_dict[chat_id]["contrast"]
        if contrast > 2.9:
            chat_dict[chat_id]["is_in_process"] = False
            return

        contrast += 0.1
        adjust_contast_brightness(call.message, contrast, brightness,
                                  is_first=False)

    elif call.data == "bright_dec":
        brightness = chat_dict[chat_id]["brightness"]
        contrast = chat_dict[chat_id]["contrast"]
        if brightness < -0.9:
            chat_dict[chat_id]["is_in_process"] = False
            return

        brightness -= 0.1
        adjust_contast_brightness(call.message, contrast, brightness,
                                  is_first=False)

    elif call.data == "bright_adj":
        brightness = chat_dict[chat_id]["brightness"]
        contrast = chat_dict[chat_id]["contrast"]
        if brightness > 2.9:
            chat_dict[chat_id]["is_in_process"] = False
            return

        brightness += 0.1
        adjust_contast_brightness(call.message, contrast, brightness,
                                  is_first=False)

    chat_dict[chat_id]["is_in_process"] = False
