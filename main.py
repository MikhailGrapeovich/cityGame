import os.path
from typing import Tuple
import json
import geonamescache
import requests
import telebot
import wikipedia
import dataBase as db

TOKEN = "7066282025:AAG9Qp3QGT0Eg987XL1O7a596W07srignXI"
bot = telebot.TeleBot(TOKEN)
used_cities = []
geo = geonamescache.GeonamesCache()
cities = geo.get_cities()
wrong_letters = ["ё", "й", "ь", "ъ"]
write_file_extensions = [".jpeg", ".jpg", ".png"]
API_KEY = "7de58748f998310072093e827a132fbd"
guide_url = "https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude={part}&appid={API key}"

class User:
    def __init__(self, chat_id, score, cities):
        self.chat_id = chat_id
        self.score = score
        self.cities = json.loads(cities)
    def save(self):
        db.update_db(self.chat_id, self.score, json.dumps(self.cities))

def get_weather(lat, lon):
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}")
    print(response.text)
@bot.message_handler(commands=["start"])
def start(message):
    if  db.get_db(message.chat.id) is None:
        db.add_db(message.chat.id, 0, dict())
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
    user = User(*db.get_db(message.chat.id))
    name_city = message.text
    letter = message.text[-1]
    search_city = geo.search_cities(name_city)
    if not search_city:
        bot.send_message(message.chat.id, "Такого города не существует, выберай другой!")
    else:
        id_city = str(search_city[0].get("geonameid"))
        if id_city in user.cities:
            bot.send_message(message.chat.id, "Такой город был!")
            return None
        if user.cities:
            if name_city[0].lower() != list(user.cities.values())[-1][-1].lower():
                bot.send_message(message.chat.id, f"Я же сказал тебе на {list(user.cities.values())[-1][-1]}")
                return
        if letter in wrong_letters:
            letter = message.text[-2]

        bot.send_message(message.chat.id, "Да, такой город есть")
        user.cities[id_city] = name_city
        bot.send_message(message.chat.id, f"Я должен сказать город на букву: {letter}")
        city_id, found_city, lat, long = find_city(letter, user)

        get_weather(lat, long)
        bot.send_message(message.chat.id, found_city)
        bot.send_location(message.chat.id, lat, long)
        info = get_city_info(found_city)
        if info is None:
            bot.send_message(message.chat.id, "информация не найдена")
        else:
            bot.send_message(message.chat.id, info)

        image = get_image(found_city)
        if image is None:
            bot.send_message(message.chat.id, "фото не найдено")
        else:
            bot.send_photo(message.chat.id,image)
        bot.send_message(message.chat.id, f"Тебе на {found_city[-1]}")
        user.save()


def find_city(letter: str, user) -> Tuple[str | None, str | None, int, int]:
    for city in cities.values():
        names = city.get("alternatenames")
        city_id = str(city.get("geonameid"))
        for name in names:
            if name:
                if name[0] == letter.upper():
                    if city_id in user.cities:
                        continue
                    user.cities[city_id] = name
                    user.save()
                    shirota = city.get("latitude")
                    dolgota = city.get("longitude")
                    return city_id, name, shirota, dolgota
    return None, None, 0, 0

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
