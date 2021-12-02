import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_total_page_count(url):
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, 'lxml')

        total_pages = soup.find('ul', class_='pagination').find('li', class_='next').find_previous_sibling().\
                    text.strip()

        return int(total_pages)
    else:
        raise Exception("НЕ УДАЛОСЬ РАСПАРСИТЬ БАЗОВЫЙ URL. ПРОВЕРЬТЕ ПОДКЛЮЧЕНИЕ")


def write_csv(data):
    with open('coins.csv', 'a', encoding="utf-8") as file:
        order = ['coin_name', 'coin_ticker', 'coin_market_cap', 'coin_price', 'coin_url']
        writer = csv.DictWriter(file, fieldnames=order)
        writer.writerow(data)


def get_page_html(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(argument="--log-level=3")
    chrome_options.add_argument(argument="--headless")
    driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)

    driver.get(url)
    trs_generator = [f'/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div[5]/table/tbody/tr[{tr_number}]'
    for tr_number in range(1, 101, 15)]
    WebDriverWait(driver, 40).until(EC.presence_of_element_located(
        (By.XPATH,'/html/body/div[1]/div/div[1]/div[2]/div/div[1]/div[5]/table/tbody/tr[1]')
        ))
    
    for tr in trs_generator:
        row = driver.find_element_by_xpath(tr)
        ActionChains(driver).move_to_element(row).perform()
    
    html = driver.page_source
 
    if html:
        return html
    return None


def clear(s: str):
    ''' work with string like $1,234.56 --> 1234.56'''
    new_str = s.replace('$', '').replace(',', '').strip()
    return new_str


def parse_url(html):
    soup = BeautifulSoup(html, 'lxml')

    rows = soup.find('tbody').find_all('tr')

    for row in rows:
        tds = row.find_all('td')

        try:
            coin_name = tds[2].find('p', {'color': 'text'}).text
        except:
            coin_name = '' 

        try:
            coin_ticker = tds[2].find('p', {'color': 'text3'}).text
        except:
            coin_ticker = ''

        try:
            coin_price = clear(tds[3].find('span').text)
        except:
            coin_price = ''

        try:
            coin_market_cap = clear(tds[6].find('span', class_='ieFnWP').text)
        except:
            coin_market_cap = ''

        try:
            coin_url = 'https://coinmarketcap.com' + tds[2].find('a').get('href').strip()
        except:
            coin_url = ''

        data = {
            'coin_name': coin_name,
            'coin_ticker': coin_ticker,
            'coin_market_cap': coin_market_cap,
            'coin_price': coin_price,
            'coin_url': coin_url
        }
        write_csv(data)

def main():
    base_url = "https://www.coinmarketcap.com"
    total_page_count = get_total_page_count(base_url)

    url_generator = [f'https://coinmarketcap.com/?page={page}' for page in range(1, total_page_count+1)]

    for url in url_generator:
        parse_url(get_page_html(url))


if __name__ == "__main__":
    main()