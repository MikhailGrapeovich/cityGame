import telebot
import geonamescache
TOKEN = "7066282025:AAG9Qp3QGT0Eg987XL1O7a596W07srignXI"
bot = telebot.TeleBot(TOKEN)
used_cities = []
geo = geonamescache.GeonamesCache()
cities = geo.get_cities()
print(cities)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Игра начата, называйте город первым")

@bot.message_handler(commands=["stop"])
def start(message):
    bot.send_message(message.chat.id, "Игра остановлена")

@bot.message_handler(commands=["help"])
def start(message):
    bot.send_message(message.chat.id, "Напишите '/start' чтобы начать игру,\nили воспользуйтесь командой '/stop' чтобы остановить игру.\n")

@bot.message_handler(content_types=["text"])
def answer(message):
    if not geo.search_cities(message.text):
        bot.send_message(message.chat.id,"Такого города не существует, выберай другой!")
    else:
        bot.send_message(message.chat.id,"Да, такой город есть")