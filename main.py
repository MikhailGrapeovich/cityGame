import telebot
import geonamescache

TOKEN = "7066282025:AAG9Qp3QGT0Eg987XL1O7a596W07srignXI"
bot = telebot.TeleBot(TOKEN)
used_cities = []
geo = geonamescache.GeonamesCache()
cities = geo.get_cities()


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Игра начата, называйте город первым")


@bot.message_handler(commands=["stop"])
def start(message):
    bot.send_message(message.chat.id, "Игра остановлена")


@bot.message_handler(commands=["help"])
def start(message):
    bot.send_message(message.chat.id,
                     "Напишите '/start' чтобы начать игру,\nили воспользуйтесь командой '/stop' чтобы остановить игру.\n")


@bot.message_handler(content_types=["text"])
def answer(message):
    city = message.text
    letter = message.text[-1]
    if not geo.search_cities(city):
        bot.send_message(message.chat.id, "Такого города не существует, выберай другой!")
    else:
        bot.send_message(message.chat.id, "Да, такой город есть")
        bot.send_message(message.chat.id, f"Я должен сказать город на букву: {letter}")
        found_city = find_city(letter)
        bot.send_message(message.chat.id, found_city)
        bot.send_message(message.chat.id, f"Тебе на {found_city[-1]}")


def find_city(letter: str):
    for city in cities.values():
        names = city.get("alternatenames")
        for name in names:
            if name[0] == letter.upper():
                return name


bot.infinity_polling()
