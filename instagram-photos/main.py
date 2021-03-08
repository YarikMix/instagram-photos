import yaml
import requests
import threading
import time
from tqdm import tqdm
from pathlib import Path

from instabot import Bot
from pytils import numeral


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR.joinpath("config.yaml")

with open(CONFIG_PATH, encoding="utf-8") as ymlFile:
    config = yaml.load(ymlFile.read(), Loader=yaml.Loader)


class InstDownloader:
    def __init__(self, target):
        self.target = target
        self.photos_path = BASE_DIR.joinpath("photos")
        self.user_photos_path = self.photos_path.joinpath(self.target)

    def auth(self):
        self.bot = Bot()
        self.bot.login(
            username=config["instagram"]["username"],
            password=config["instagram"]["password"]
        )

    @staticmethod
    def delete_cookies():
        """Удаляет кукисы"""
        cookies = BASE_DIR.joinpath(f"config/{config['instagram']['username']}_uuid_and_cookie.json")
        if cookies.exists():
            cookies.unlink()

    def download_photo(self, media_id):
        """Скачиваем все фото с посто по его id"""
        media = self.bot.get_media_info(media_id)[0]
        # Если в посте одна фотография
        if("image_versions2" in media.keys()):
            photo_id = media["id"]
            photo_url = media["image_versions2"]["candidates"][0]["url"]
            photo_path = self.user_photos_path.joinpath(f"{photo_id}.jpg")
            if not photo_path.exists():
                response = requests.get(photo_url)
                with open(photo_path, "wb") as f:
                    response.raw.decode_content = True
                    f.write(response.content)
        # Если в посте несколько фотографий
        elif("carousel_media" in media.keys()):
            for e, element in enumerate(media["carousel_media"]):
                photo_id = media["id"]
                photo_url = element['image_versions2']["candidates"][0]["url"]
                photo_path = self.user_photos_path.joinpath(f"{photo_id}_{e}.jpg")
                if not photo_path.exists():
                    response = requests.get(photo_url)
                    with open(photo_path, "wb") as f:
                        response.raw.decode_content = True
                        f.write(response.content)

        self.lock.release()

    def download_photos(self, media_ids):
        # Number of parallel threads
        self.lock = threading.Semaphore(4)

        # List of threads objects I so we can handle them later
        thread_pool = []

        pbar = tqdm(total=len(media_ids))
        for media_id in media_ids:
            thread = threading.Thread(target=self.download_photo, args=(media_id,))
            thread_pool.append(thread)
            thread.start()

            # Add one to our lock, so we will wait if needed.
            self.lock.acquire()

            pbar.update(1)

        pbar.close()

        for thread in thread_pool:
            thread.join()

    def get_photos(self):
        # Получаем id всех постов
        media_ids = self.bot.get_total_user_medias(user_id=self.target)

        if len(media_ids) == 0:
            print("Пользователя с таким именем не существует")
            exit()

        # Создаём папку с фотографиями пользователя, если её нет
        if not self.user_photos_path.exists():
            self.user_photos_path.mkdir()
            print(f"Создаём папку с фотографиями {self.target}")
            
        print("{} {} {}".format(
            numeral.choose_plural(len(media_ids), "Будет, Будут, Будут"),
            numeral.choose_plural(len(media_ids), "скачена, скачены, скачены"),
            numeral.get_plural(len(media_ids), "фотография, фотографии, фотографий")
        ))

        time_start = time.time()
        self.download_photos(media_ids)

        time_finish = time.time()
        download_time = round(time_finish - time_start)
        print("{} {} за {}".format(
            numeral.choose_plural(len(media_ids), "Скачена, Скачены, Скачены"),
            numeral.get_plural(len(media_ids), "фотография, фотографии, фотографий"),
            numeral.get_plural(download_time, "секунду, секунды, секунд")
        ))

    def main(self):
        # Удаляем кукисы
        self.delete_cookies()

        # Создаём папку с фотографиями, если её нет
        if not self.photos_path.exists():
            self.photos_path.mkdir()

        self.auth()

        try:
            self.get_photos()
        except:
            print("Пользователя с таким именем не существует")

        # Удаляем кукисы
        self.delete_cookies()


if __name__ == "__main__":
    username = input("Введите никнейм\n> ")
    downloader = InstDownloader(target=username)
    downloader.main()