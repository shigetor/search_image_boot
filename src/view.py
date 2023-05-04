import logging
import os
from os.path import isfile, join
from aiogram import Bot, Dispatcher, executor, types
from icrawler.builtin import GoogleImageCrawler

from settings import bot

import time
import pyautogui as pg
from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib.request

logging.basicConfig(level=logging.INFO)

dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def echo(message: types.Message):
    await message.reply('Привет! Я бот который ищет изображения \n Для получения информации введите /help')


@dp.message_handler(commands=['help'])
async def echo(message: types.Message):
    await message.reply('Просто отправьте мне изображение, и я постараюсь найти вам похожие')


@dp.message_handler(content_types=[types.ContentType.PHOTO])
async def download_photo(message: types.Message):
    path_send_photos = f"photos/{message.chat.id}/"
    if not os.path.isdir(f"photos/{message.from_user.id}/"):
        os.mkdir(f"photos/{message.from_user.id}/")

    if not os.path.isdir(f"photos/download/{message.from_user.id}/"):
        os.mkdir(f"photos/download/{message.chat.id}")
    await message.photo[-1].download(destination_dir=f'photos/{message.from_user.id}')

    await message.answer(f"Ищу похожие картинки")
    options = webdriver.ChromeOptions()

    options.add_argument("--disable-infobars")
    options.add_argument("start-maximized")
    options.add_argument("--disable-extensions")
    path_photo = f"photos/{message.chat.id}/photos/"

    driver = webdriver.Chrome(chrome_options=options)
    driver.implicitly_wait(10)
    driver.get("https://images.google.com/")

    driver.find_element(By.XPATH, "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[3]/div[4]").click()
    driver.find_element(By.XPATH,
                        "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[3]/c-wiz/div[2]/div/div[3]/div[2]/div/div[2]/span").click()
    time.sleep(3)
    res_img = [f for f in os.listdir(path_photo) if isfile(join(path_photo, f))]
    pg.write(fr"C:\Users\kozyr\PycharmProjects\Image_searcher_bot\src\photos\{message.chat.id}\photos\{res_img[-1]}")
    pg.press('enter')
    time.sleep(10)

    images = driver.find_elements(By.TAG_NAME, 'img')
    for image in range(5, 10, 2):
        src = images[image].get_attribute('src')
        if src.startswith('https'):
            urllib.request.urlretrieve(src, f"photos/download/{message.chat.id}/file_name_{image}.jpg")

    time.sleep(7)

    path_photo_download = f"photos/download/{message.chat.id}/"
    res_for_download = os.listdir(path_photo_download)

    path_send_photos = f"photos/{message.chat.id}/photos/"
    res_for_sen_photos = os.listdir(path_send_photos)
    for item in res_for_download:
        await bot.send_photo(chat_id=message.chat.id, photo=open(f'photos/download/{message.chat.id}/{item}', 'rb'))
    for i in res_for_download:
        os.remove(os.path.join(path_photo_download, i))
    for i in res_for_sen_photos:
        os.remove(os.path.join(path_send_photos, i))


@dp.message_handler(commands=['photo'])
async def cmd_name(message: types.Message):
    google_crawler = GoogleImageCrawler(storage={'root_dir': f'photos/send_photos/{message.chat.id}/'})

    google_crawler.crawl(keyword=f'{message.text}', max_num=10)
    path_photo = f"photos/send_photos/{message.chat.id}/"
    res = os.listdir(path_photo)

    for item in res:
        await bot.send_photo(chat_id=message.chat.id, photo=open(f'photos/send_photos/{message.chat.id}/{item}', 'rb'))
    # time.sleep(10)
    for i in res:
        os.remove(os.path.join(path_photo, i))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
