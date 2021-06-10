
import json

import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time


class ReviewScraper():
    def __init__(self):
        self.driver = self.__get_driver()

    def __get_driver(self,debug=True):
        options = Options()

        if not debug:
            options.add_argument("--headless")
            options.add_argument('--no-sandbox')
        else:
            options.add_argument("--window-size=1366,768")
            options.add_argument('--no-sandbox')

        options.add_argument("--disable-notifications")
        options.add_argument("--lang=en-US")
        driv_path = '../config/webdrivers/chromedriver.exe'
        input_driver = webdriver.Chrome(options=options, executable_path=driv_path)
        print('Driver Got')
        return input_driver
    def __sort_review(self):
        wait = WebDriverWait(self.driver, 10)

        menu_bt = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-value=\'Sort\']')))
        menu_bt.click()
        time.sleep(1)
        recent_rating_bt = self.driver.find_elements_by_xpath('//li[@role=\'menuitemradio\']')[1]
        recent_rating_bt.click()
        time.sleep(1)
        print('Reviews Sorted')

    def __goto_review(self):
        links = self.driver.find_elements_by_xpath('//button[@jsaction=\'pane.reviewChart.moreReviews\']')
            # print(links)
        for l in links:
            # print("Element is visible? " + str(l.is_displayed()))
            l.click()
            time.sleep(2)

    def __scroll(self):
        reviews_divs = self.driver.find_elements_by_class_name('section-layout')
        reviews_divs[-1].click()
        scrollable_div = self.driver.find_element_by_css_selector(
            'div.section-layout.section-scrollbox.mapsConsumerUiCommonScrollable__scrollable-y.mapsConsumerUiCommonScrollable__scrollable-show')
        #
        # self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        # print(self.driver.execute_script("return document.body.scrollTop"))
        # print(self.driver.execute_script("return document.documentElement.scrollHeight"))
        height = self.driver.execute_script("return document.documentElement.scrollHeight",scrollable_div)
        print(height)
        self.driver.execute_script("window.scrollTo(0, " + str(height) + ");")
        time.sleep(2)

    def __expand_reviews(self):
        links = self.driver.find_elements_by_xpath('//button[@class=\'section-expand-review mapsConsumerUiCommonButton.blue-link\']')
        for l in links:
            l.click()
            time.sleep(0.5)
            print('Review Expanded')

    def url_setup(self,url):
        self.driver.get(url)
        time.sleep(2)
        self.__goto_review()
        self.__sort_review()

    def get_reviews_block(self, offset,cbg):

        # scroll to load reviews

        self.__scroll()

        self.__expand_reviews()

        resp = BeautifulSoup(self.driver.page_source, 'html.parser')

        rblock = resp.find_all('div', class_='section-review-text')
        parsed_reviews = []
        for index, review in enumerate(rblock):
            if index >= offset:
                parsed_reviews.append(self.parse_review(review,cbg))
                # print(self.parse_review(review,cbg))

        return parsed_reviews

    # def parse_fname(self, fpath):


    def get_reviews(self, N, url,cbg,place_id):
        self.url_setup(url)

        n = 0
        all_revs = []

        while (n < N):

            reviews = self.get_reviews_block( n,cbg)

            for r in reviews:
                all_revs.append(r)
            dpath = '../data/outputs/reviews/'
            os.makedirs(dpath, exist_ok=True)
            fpath = dpath + str(cbg)+ '_' + place_id + '.json'
            with open(fpath, 'w') as outfile:
                json.dump(all_revs, outfile, indent=4)
            n += len(reviews)
        return all_revs

    def filter_string(self, str):
        strOut = str.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ').replace("\\","")
        return strOut

    def parse_review(self,review,cbg):

        item = {}

        id_review = review.find('button', class_='section-review-action-menu')['data-review-id']
        username = review.find('div', class_='section-review-title').find('span').text

        try:
            review_text = self.filter_string(review.find('span', class_='section-review-text').text)
        except Exception as e:
            review_text = None

        rating = float(review.find('span', class_='section-review-stars')['aria-label'].split(' ')[1])
        relative_date = review.find('span', class_='section-review-publish-date').text

        try:
            n_reviews_photos = review.find('div', class_='section-review-subtitle').find_all('span')[1].text
            metadata = n_reviews_photos.split('\xe3\x83\xbb')
            if len(metadata) == 3:
                n_photos = int(metadata[2].split(' ')[0].replace('.', ''))
            else:
                n_photos = 0

            idx = len(metadata)
            n_reviews = int(metadata[idx - 1].split(' ')[0].replace('.', ''))

        except Exception as e:
            n_reviews = 0
            n_photos = 0

        user_url = review.find('a')['href']

        item['id_review'] = id_review
        item['caption'] = review_text

        item['relative_date'] = relative_date
        todays_date = datetime.now()
        item['retrieval_date'] =datetime.strftime(todays_date,format = '%Y-%m-%d')
        item['rating'] = rating
        item['username'] = username
        item['n_review_user'] = n_reviews
        item['n_photo_user'] = n_photos
        item['url_user'] = user_url
        item['census_block_group'] = cbg


        return item

    def get_place_data(self,url):

        self.driver.get(url)

        # ajax call also for this section
        time.sleep(2)
        place = {}
        resp = BeautifulSoup(self.driver.page_source, 'html.parser')
        try:
            place['overall_rating'] = float(resp.find('div', class_='gm2-display-2').text.replace(',', '.'))
        except:
            place['overall_rating'] = 'NOT FOUND'

        try:
            place['n_reviews'] = int(self.driver.find_elements_by_xpath('//button[@jsaction=\'pane.reviewChart.moreReviews\']')[0].text.split(' ')[0])
        except:
            place['n_reviews'] = 0

        return place