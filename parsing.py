import html

import numpy as np
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.by import By

LAST_PAGE_NUMBER = 55


def parse_string(input_string, start_string, end_string):
    start_index = input_string.find(start_string)
    if start_index == -1:
        return None
    start_index += len(start_string)

    end_index = input_string.find(end_string, start_index)
    if end_index == -1:
        return None

    parsed_string = input_string[start_index:end_index]
    return parsed_string


options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
# options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

df = pd.DataFrame(
    columns=['index', 'href', 'title', 'price', 'zalog', 'predoplata', 'komissiya' 'area', 'floor',
             'totalArea', 'kitchenArea', 'livingArea', 'roomsCount', 'hasAirConditioner', 'hasDishwasher',
             'hasFridge', 'hasFurniture', 'hasInternet', 'hasKitchenFurniture', 'hasTv',
             'hasWashingMachine', 'hasBalcony', 'ceilingHeightM', 'routesList', 'windowsDirection', 'ceilingHeightM'])
df = df.set_index('index')


def parse_page(page_number, df):
    url = f'https://m2.ru/moskva/nedvizhimost/snyat-kvartiru/?pageNumber={page_number}'
    driver.get(url)
    start = len(df)
    elements = driver.find_elements(By.CLASS_NAME, 'OffersSearchList__item')
    for element in elements:
        ind = len(df)
        try:
            text_elem = element.get_attribute('innerHTML')
            df.loc[ind] = [None] * len(df.columns)
            payment = parse_string(text_elem, 'LayoutSnippet__paymentsInfo', 'LayoutSnippet')
            df.loc[ind, 'index'] = int(len(df))
            df.loc[ind, 'title'] = parse_string(text_elem, 'img alt="', '"')
            df.loc[ind, 'zalog'] = parse_string(payment, 'Залог', '<') if payment is not None else None
            df.loc[ind, 'predoplata'] = parse_string(payment, 'Предоплата', '<') if payment is not None else None
            df.loc[ind, 'komissiya'] = parse_string(payment, 'Комиссия', '<') if payment is not None else None
            df.loc[ind, 'price'] = parse_string(text_elem, 'offer-price"><span itemprop="price" content="', '"')
            df.loc[ind, 'href'] = parse_string(text_elem, 'href="', '"')
        except:
            df = df.drop(ind)
    print(df)
    for i in range(start, len(df)):
        try:
            driver.get(df.loc[i]['href'])
            df.loc[i, 'totalArea'] = parse_string(driver.page_source, 'totalArea', ',"unit').split(':')[-1]
            df.loc[i, 'kitchenArea'] = parse_string(driver.page_source, 'kitchenArea', ',"unit').split(':')[-1]
            df.loc[i, 'livingArea'] = parse_string(driver.page_source, 'livingArea":{"formatted":"', '"')
            df.loc[i, 'roomsCount'] = parse_string(driver.page_source, 'roomsCount":', ',')
            df.loc[i, 'floor'] = parse_string(driver.page_source, 'floor":', ',')
            df.loc[i, 'hasAirConditioner'] = parse_string(driver.page_source, 'hasAirConditioner":', ',')
            df.loc[i, 'hasDishwasher'] = parse_string(driver.page_source, 'hasDishwasher":', ',')
            df.loc[i, 'hasFridge'] = parse_string(driver.page_source, 'hasFridge":', ',')
            df.loc[i, 'hasFurniture'] = parse_string(driver.page_source, 'hasFurniture":', ',')
            df.loc[i, 'hasInternet'] = parse_string(driver.page_source, 'hasInternet":', ',')
            df.loc[i, 'hasKitchenFurniture'] = parse_string(driver.page_source, 'hasKitchenFurniture":', ',')
            df.loc[i, 'hasTv'] = parse_string(driver.page_source, 'hasTv":', ',')
            df.loc[i, 'hasWashingMachine'] = parse_string(driver.page_source, 'hasWashingMachine":', '}')
            df.loc[i, 'hasBalcony'] = parse_string(driver.page_source, 'hasBalcony":', ',')
            df.loc[i, 'ceilingHeightM'] = parse_string(driver.page_source, 'hasBalcony":', ',')
            df.loc[i, 'routesList'] = parse_string(driver.page_source, '"routesList":[', '}]')
            df.loc[i, 'windowsDirection'] = parse_string(driver.page_source, '"windowsDirection":"', '"')
            df.loc[i, 'ceilingHeightM'] = parse_string(driver.page_source, '"ceilingHeightM":"', '"')

            for col in df.columns:
                try:
                    df.loc[i, col] = html.unescape(df.loc[i, col]).strip()
                except:
                    pass
        except:
            pass


for j in range(LAST_PAGE_NUMBER):
    parse_page(j, df)

driver.quit()

df.to_csv('result.csv', index=False, encoding='UTF-8')
