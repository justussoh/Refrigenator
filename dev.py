import logging
import datetime
from ocr import *
from fridge import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, PhotoSize
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler,ConversationHandler, InlineQueryHandler, JobQueue, RegexHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
knownUser = {}
commands = {
    "start" : 'Initialise User',
    "help" : 'Gives you information about the available commands',
    "add" : "Adds food item into your fridge",
    "used" : "Removes food item from fridge",
    "display" : "See what's in your Fridge",
    "clear" : "Resets your fridge",
    "scan" : "Send a photo of your receipt",
    "addexpiry" : "Add expiry date for items"
 }

#/start

def start(bot, update):
    cid = update.message.chat_id
    if cid not in knownUser:
        fridge = Fridge()
        knownUser[cid]=fridge
        bot.send_message(chat_id=cid, text="Hello! This bot helps you to reduce food wastage by managing your fridge.")
        #create a instance of fridge
    else:
        bot.send_message(chat_id=cid, text="User Data already stored!")
    help(bot, update)

#/Help

def help(bot, update):
    cid = update.message.chat_id
    help_text = "The following commands are available: \n"
    for key in commands.keys():
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(chat_id=cid, text=help_text)

#USED FOR /Add

cat = ["FRUITS", "VEGETABLES", "MEAT", "DAIRY PRODUCTS", "OTHERS"]
CAT, FOOD, OTHERS, EXPIRE= range(4)

def add(bot, update):
    keyboard = [[InlineKeyboardButton(text= k, callback_data = k)] for k in cat]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('What would you like to add? \n Please choose:', reply_markup=reply_markup)
    return CAT

def button(bot, update, user_data):
    query = update.callback_query
    cid = query.message.chat_id
    cat = knownUser[cid].get_category(query.data)
    user_data["Cat"]= query.data
    keyboard = [[InlineKeyboardButton(text= k, callback_data = k)] for k in cat]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(text="{} Selected".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id, reply_markup=reply_markup)
    return FOOD

def button1(bot, update, user_data):
    query = update.callback_query
    if query.data== "Others":
        bot.edit_message_text(text="What is the item?",
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        return OTHERS
    else:
        user_data["fruit"]= query.data
        keyboard = [["1","2","3"],["4","5","6"], ["7", "8", "9"],["0",]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard= True, one_time_keyboard= True)
        bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
        bot.send_message(chat_id=query.message.chat_id, text= "How many days to expiry?", reply_markup = reply_markup)
        return EXPIRE

def newItem(bot, update, user_data):
    text = update.message.text.upper()
    user_data['fruit'] = text
    cid=update.message.chat_id
    knownUser[cid].add_entry_to_cat(text, user_data["Cat"])
    keyboard = [["1","2","3"],["4","5","6"], ["7", "8", "9"],["0",]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard= True, one_time_keyboard= True)
    bot.send_message(chat_id=cid, text= "When will it expire?", reply_markup= reply_markup)
    return EXPIRE

def expire(bot, update, user_data):
    text = update.message.text
    user_data['expire'] = text
    new= Food(user_data["fruit"], int(user_data['expire']), user_data["Cat"]) #food inital
    cid=update.message.chat_id
    knownUser[cid].add_food(new) #add food to fridge
    bot.send_message(chat_id=cid, text= "Item Successfully Added")
    return ConversationHandler.END

def cancel(bot, update):
    update.message.reply_text('Bye!')
    return ConversationHandler.END

#/remove
USED , REMOVED = range(2)
cat = ["FRUITS", "VEGETABLES", "MEAT", "DAIRY PRODUCTS", "OTHERS"]

def used(bot, update):
    cid = update.message.chat_id
    keyboard = [[InlineKeyboardButton(text= k, callback_data = k)] for k in cat]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose what you want to remove:', reply_markup=reply_markup)
    return USED

def button2(bot, update, user_data):
    query = update.callback_query
    cid = query.message.chat_id
    cat = knownUser[cid].print_by_category(query.data) #get whole inventory for fride
    keyboard = [[InlineKeyboardButton(text= k, callback_data = k)] for k in cat]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text('Please choose what you would like to remove:',
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id, reply_markup=reply_markup)
    return REMOVED

def remove(bot, update, user_data):
    query = update.callback_query
    cid = query.message.chat_id
    knownUser[cid].remove_food(query.data) #remove food
    bot.edit_message_text(text="{} has been removed".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
    return ConversationHandler.END

#/dísplay
def display(bot, update):
    cid = update.message.chat_id
    res = knownUser[cid].print_full_fridge() #print food name list
    bot.send_message(chat_id=cid, text=res)

#/time

def alert(bot,job):
    for k,v in knownUser.items():
        res = v.daily_update() #Get list of expired
        try:
            bot.send_message(chat_id=k, text = res)
        except:
            continue

#/clear
CLEAR = 0

def clear(bot, update):
    cid = update.message.chat_id
    keyboard = [["Yes"],["No"]]
    reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard = True, one_time_keyboard = True)
    update.message.reply_text('Are you sure you want to clear your fridge?', reply_markup = reply_markup)
    return CLEAR

def cfm_Clear(bot, update):
    text = update.message.text
    cid=update.message.chat_id
    if text == "Yes":
        knownUser[cid].clear()
        keyboard = [[InlineKeyboardButton(text= k, callback_data = k)] for k in cat]
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(chat_id=cid, text= "Fridge has been cleared")
        return ConversationHandler.END
    else:
        return ConversationHandler.END

#/scan
PICTURE=0
def scan(bot, update):
    cid = update.message.chat_id
    update.message.reply_text('Please send me a picture!')
    return PICTURE
scan_res = []
def image_handler(bot, update):
    #file = bot.getFile(update.message.photo.file_id)
    #file_id = update.message.photo.file_id
    cid = update.message.chat_id
    file = bot.getFile(update.message.photo[-1].file_id)
    file.download('image.jpg')
    text = convert_image("C:/Users/justu/Desktop/H&R/image.jpg")
    text= knownUser[cid].add_bulk(text)

    global scan_res
    scan_res.extend(text)

    res= ""
    for i in range(len(text)):
        res += str(i+1) + ". " + text[i][0] + " \n"
    bot.send_message(chat_id=cid, text= "These items are temporary added please add a expiry date to confirm your item! \n" + res)
    return ConversationHandler.END

#/addexpiry
CHOOSE, ADDITEM, CHOOSE2 = range(3)

def make():
    list2= list(map(lambda x: x[0], scan_res))
    keyboard2 = [[InlineKeyboardButton(text= k, callback_data = k)] for k in list2]
    keyboard2.append([InlineKeyboardButton(text= "Done", callback_data = "Done")])
    reply_markup2 = InlineKeyboardMarkup(keyboard2)
    return reply_markup2

def addexpiry(bot, update):
    cid=update.message.chat_id
    bot.send_message(chat_id=cid, text= "Please add an expiry duration!",reply_markup= make())
    return CHOOSE

def choose(bot,update):
    cid=update.message.chat_id
    bot.send_message(chat_id=cid, text= "Please add an expiry duration!",reply_markup= make())
    return ADDITEM

def exp(bot, update, user_data):
    query = update.callback_query
    if query.data != "Done":
        user_data["fruit"]= query.data
        keyboard = [["1","2","3"],["4","5","6"], ["7", "8", "9"],["0",]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard= True, one_time_keyboard= True)
        bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)
        bot.send_message(chat_id=query.message.chat_id, text= "How many days to expiry?", reply_markup = reply_markup)
        return ADDITEM
    else:
        bot.send_message(chat_id=query.message.chat_id, text= "Items have been successfully added")
        return ConversationHandler.END

def newItem2(bot, update, user_data):
    text = update.message.text
    user_data['expire'] = text
    global scan_res
    for i in scan_res:
        if i[0] == user_data["fruit"]:
            res=i[1]
            scan_res.remove(i)
    new= Food(user_data["fruit"], int(user_data['expire']), res) #food inital
    cid=update.message.chat_id
    knownUser[cid].add_food(new) #add food to fridge
    bot.send_message(chat_id=cid, text= "Item Successfully Added")
    return CHOOSE2

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("543071184:AAENZ26FRD-39j3IaHvVQt3R2fvC0Ytlu_8")
    j = updater.job_queue
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("display", display))
    #dp.add_handler(CommandHandler("add", add))
    #dp.add_handler(CallbackQueryHandler(button))

    conv_handler_add = ConversationHandler(

        entry_points=[CommandHandler('add', add)],

        states={CAT: [CallbackQueryHandler(button ,pass_user_data = True)],
        FOOD : [CallbackQueryHandler(button1 ,pass_user_data = True)],
        OTHERS: [MessageHandler(Filters.text, newItem, pass_user_data = True)],
        EXPIRE: [MessageHandler(Filters.text, expire, pass_user_data = True)]


        },


        fallbacks=[CommandHandler('cancel', cancel)])

    dp.add_handler(conv_handler_add)

    conv_handler_used = ConversationHandler(

        entry_points=[CommandHandler('used', used)],

        states={USED: [CallbackQueryHandler(button2 ,pass_user_data = True)],
        REMOVED: [CallbackQueryHandler(remove ,pass_user_data = True)]

        },


        fallbacks=[CommandHandler('cancel', cancel)])

    dp.add_handler(conv_handler_used)

    conv_handler_clear = ConversationHandler(

        entry_points=[CommandHandler('clear', clear)],

        states={CLEAR: [MessageHandler(Filters.text, cfm_Clear)]

        },


        fallbacks=[CommandHandler('cancel', cancel)])

    dp.add_handler(conv_handler_clear)

    conv_handler_scan = ConversationHandler(

        entry_points=[CommandHandler('scan', scan)],

        states={PICTURE: [MessageHandler(Filters.photo, image_handler)],

        },


        fallbacks=[CommandHandler('cancel', cancel)])

    dp.add_handler(conv_handler_scan)

    conv_handler_addexpiry = ConversationHandler(

        entry_points=[CommandHandler('addexpiry', addexpiry)],

        states={CHOOSE: [CallbackQueryHandler(exp ,pass_user_data = True)],
        ADDITEM:[MessageHandler(Filters.text, newItem2, pass_user_data = True)],
        CHOOSE2: [CallbackQueryHandler(choose ,pass_user_data = True)]

        },


        fallbacks=[CommandHandler('cancel', cancel)])

    dp.add_handler(conv_handler_addexpiry)

    # log all errors
    dp.add_error_handler(error)

    #Schedule Jobs
    j.run_daily(alert, datetime.time(8,0,0))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
