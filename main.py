import time
import concurrent.futures
from selenium import webdriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import json


# driver = uc.Firefox()
# driver.get('https://megamarket.ru/catalog/noutbuki/')

threads = []

class SMMParse:
    def __init__(self, url: str, count: int = 100):
        self.url = url
        self.count = count
        self.data = []

    def __set_up(self):
        options = Options()
        options.add_argument('--headless')
        self.driver = uc.Firefox(options=options)

    def __close_browser(self):
        self.driver.quit()

    def __get_url(self):
        self.driver.get(self.url)

    def __paginator(self):
        while self.driver.find_elements(By.CSS_SELECTOR, "li.next > a:nth-child(1)") and self.count > 0:
            self.__parse_page()
            try:
                self.driver.find_element(By.CSS_SELECTOR, "li.next > a:nth-child(1)").click()
            except Exception:
                print('Была ошибка')
                time.sleep(5)
                continue
            self.count -= 1
            time.sleep(3)

    def __parse_page(self):
        titles = self.driver.find_elements(By.CSS_SELECTOR, "[class = 'catalog-item-regular-desktop ddl_product catalog-item-desktop']")
        for title in titles:
            name = title.find_element(By.CSS_SELECTOR, "[class='catalog-item-regular-desktop__title-link ddl_product_link']").text
            price = title.find_element(By.CSS_SELECTOR, "[class='catalog-item-regular-desktop__price']").text
            url = title.find_element(By.CSS_SELECTOR, "[class='catalog-item-regular-desktop__title-link ddl_product_link']").get_attribute("href")
            try:
                bonus = title.find_element(By.CSS_SELECTOR, "[class='bonus-percent']").text
            except Exception:
                bonus = '0%'
            data = {
                'name': name,
                'price': price,
                'url': url,
                'bonus': bonus
            }
            # self.data.append(data)   # Запись в файл (записывает последнее, надо исправить)
            if int(bonus[:-1]) >= 40 and int(bonus[:-1]) < 50:  # Можно задать процент бонуса "!!!!!!!!!!!!!!!!!"
                print(bonus, " | ", price, " | ", name, " | ", url)
            else:
                continue

        # self.__save_data()  # Запись в файл (записывает последнее, надо исправить)

    def __save_data(self):
        with open("items.json", 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def parse(self, retry=5):
        self.__set_up()
        try:
            self.__get_url()
        except Exception:
            if retry:
                self.__close_browser()
                print('Была ошибка в get_url, жду 5 сек', retry)
                time.sleep(5)
                return self.parse(retry-1)
            else:
                print('выход pass')
                pass
        try:
            self.__paginator()
        except Exception:
            if retry:
                self.__close_browser()
                print('Была ошибка в paginator, жду 5 сек', retry)  # Тут ошибка с проверкой возраста на сайте
                time.sleep(5)
                return self.parse(retry-1)
            else:
                print('выход pass')
                pass

        self.__close_browser()


def process_url(url):
    print('Проверяю:', url, end='')
    SMMParse(url=url, count=3).parse()


if __name__ == "__main__":
    urls = []
    with open("rework_not_double.txt", "r") as file:
        urls = file.readlines()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:  # Указываю нужное количество потоков в max_workers
        executor.map(process_url, urls)