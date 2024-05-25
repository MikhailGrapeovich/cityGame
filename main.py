from typing import Union, Tuple

import requests
import os.path
import telebot
import geonamescache
import wikipedia

TOKEN = "7066282025:AAG9Qp3QGT0Eg987XL1O7a596W07srignXI"
bot = telebot.TeleBot(TOKEN)
used_cities = []
geo = geonamescache.GeonamesCache()
cities = geo.get_cities()
wrong_letters = ["ё", "й", "ь", "ъ"]
write_file_extensions = [".jpeg", ".jpg", ".png"]
API_KEY = "7de58748f998310072093e827a132fbd"
guide_url = "https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}"

def get_weather(lat, lon):
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}")
    print(response.text)
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Игра начата, называйте город первым")


@bot.message_handler(commands=["stop"])
def stop(message):
    bot.send_message(message.chat.id, "Игра остановлена")


@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id,
                     "Напишите '/start' чтобы начать игру,\nили воспользуйтесь командой '/stop' чтобы остановить игру.\n")


@bot.message_handler(content_types=["text"])
def answer(message):
    city = message.text
    letter = message.text[-1]
    if city in used_cities:
        bot.send_message(message.chat.id, "Такой город был!")
        return None
    if used_cities:
        if city[0].lower() != used_cities[-1][-1].lower():
            bot.send_message(message.chat.id, f"Я же сказал тебе на {used_cities[-1][-1]}")
            return
    if letter in wrong_letters:
        letter = message.text[-2]
    if not geo.search_cities(city):
        bot.send_message(message.chat.id, "Такого города не существует, выберай другой!")
    else:
        bot.send_message(message.chat.id, "Да, такой город есть")
        bot.send_message(message.chat.id, f"Я должен сказать город на букву: {letter}")
        found_city, lat, long = find_city(letter)
        get_weather(lat, long)
        bot.send_message(message.chat.id, found_city)
        bot.send_location(message.chat.id, lat, long)
        bot.send_message(message.chat.id, get_city_info(found_city))
        image = get_image(found_city)
        if image is None:
            bot.send_message(message.chat.id, "фото не найдено")
        else:
            bot.send_photo(message.chat.id,image)
        bot.send_message(message.chat.id, f"Тебе на {found_city[-1]}")


def find_city(letter: str) -> Tuple[str | None, int, int]:
    for city in cities.values():
        names = city.get("alternatenames")
        for name in names:
            if name:
                if name[0] == letter.upper():
                    if name in used_cities:
                        continue
                    used_cities.append(name)
                    shirota = city.get("latitude")
                    dolgota = city.get("longitude")
                    return name, shirota, dolgota
    return None, 0, 0

def decorator_wiki_request(func):
    def wrapper(city, *args, **kwargs):
        try:
            return func(city, *args, **kwargs)
        except (wikipedia.DisambiguationError, wikipedia.HTTPTimeoutError, wikipedia.PageError, wikipedia.RedirectError, wikipedia.WikipediaException):
            return None
    return wrapper

@decorator_wiki_request
def get_image(city):
    wikipedia.set_lang('ru')
    wiki_response = wikipedia.search(city)
    if wiki_response:
        wiki_page = wikipedia.page(wiki_response[0])
        for wiki_image in wiki_page.images:
            if os.path.splitext(wiki_image)[1] in write_file_extensions:
                return wiki_image
    return None
@decorator_wiki_request
def get_city_info(city):
    wikipedia.set_lang('ru')
    wiki_response = wikipedia.search(city)
    if wiki_response:
        wiki_city = wikipedia.summary(wiki_response[0])
        return wiki_city
    else:
        return f"Информация о {city} не найдена"


bot.infinity_polling()
