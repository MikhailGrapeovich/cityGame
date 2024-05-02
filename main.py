from typing import Union, Tuple

import telebot
import geonamescache
import wikipedia

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
    if city in used_cities:
        bot.send_message(message.chat.id, "Такой город был!")
        return None
    if used_cities:
        if city[0].lower() != used_cities[-1][-1].lower():
            bot.send_message(message.chat.id, f"Я же сказал тебе на {used_cities[-1][-1]}")
            return
    letter = message.text[-1]
    if not geo.search_cities(city):
        bot.send_message(message.chat.id, "Такого города не существует, выберай другой!")
    else:
        bot.send_message(message.chat.id, "Да, такой город есть")
        bot.send_message(message.chat.id, f"Я должен сказать город на букву: {letter}")
        found_city, lat, long = find_city(letter)
        bot.send_message(message.chat.id, found_city)
        bot.send_location(message.chat.id, lat, long)
        bot.send_message(message.chat.id, get_city_info(found_city))
        bot.send_message(message.chat.id, f"Тебе на {found_city[-1]}")


def find_city(letter: str) -> Tuple[str | None, int, int]:
    for city in cities.values():
        names = city.get("alternatenames")
        for name in names:
            if name[0] == letter.upper():
                if name in used_cities:
                    continue
                used_cities.append(name)
                shirota = city.get("latitude")
                dolgota = city.get("longitude")
                return name, shirota, dolgota
    return None, 0, 0


def get_city_info(city):
    wikipedia.set_lang('ru')
    wiki_response = wikipedia.search(city)
    if wiki_response:
        wiki_city = wikipedia.summary(wiki_response[0])
        return wiki_city
    else:
        return f"Информация о {city} не найдена"


bot.infinity_polling()
