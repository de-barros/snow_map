import re
from time import sleep
from random import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


URL_STOP_WORDS = ['pages', 'profile.', 'Elementary']


def find_best(res_list):
    result_likes = []
    for l in res_list:
        try:
            url = l.find_element(By.XPATH, './/h3[@class="r"]/a[@href]').get_attribute('href')
            text = l.find_element(By.XPATH, './/div[@class="s"]/div/span[@class="st"]').text
        except StaleElementReferenceException:
            break

        if any(w in url for w in URL_STOP_WORDS) or ('facebook' not in url) or ('likes' not in text):
            # print('url', url)
            # print('text', text, '\n')
            continue
        else:
            num_likes = re.findall(r'(\d+)\slikes', l.text)
            k_likes = re.findall(r'([\d\.]+)K\slikes', l.text)
            if num_likes:
                result_likes.append((url, int(num_likes[0])))
            elif k_likes:
                result_likes.append((url, int(float(k_likes[0]) * 1000)))

    sor = sorted(result_likes, key=lambda tup: tup[1], reverse=True)
    print('sorted candidates:\n', sor)
    if not sor:
        return 'NOT FOUND'

    return sor[0][0]


def get_fb_name(query):
    input_element = driver.find_element_by_name("q")
    sleep(.75 + random()-0.5)
    input_element.send_keys(query)
    sleep(.75 + random()-0.5)
    input_element.submit()
    Y = random()*1080
    driver.execute_script("window.scrollTo(0, {});".format(Y))

    RESULTS_LOCATOR = "//div[@class='rc']"
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, RESULTS_LOCATOR)))
    rcs = driver.find_elements(By.XPATH, RESULTS_LOCATOR)
    best_result = find_best(rcs)

    if len(best_result.split('/')) >= 3:
        fb_name = best_result.split('/')[3].split('?')[0]
        return fb_name
    else:
        return 'NOT FOUND'


def get_query(dist_name):
    d_words = dist_name.split(' ')
    # if name ends with "School District" search "Schools" instead
    if d_words[-2:] == ['School', 'District']:
        query = ' '.join(d_words[:-2]) + ' Schools Michigan facebook'
    else:
        query = dist_name + ' Michigan facebook'
    return query


driver = webdriver.Safari()
fb_names = []
driver.get("http://www.google.com")

with open('dists_mi.csv') as f:
    next(f)
    counter = 0
    driver.get("http://www.google.com")
    for line in f:
        dist_name = line.split(',')[0]
        query = get_query(dist_name)

        print('DISTRICT: ', dist_name)
        fb_name = get_fb_name(query)
        print('\nResult:', fb_name)
        fb_names.append(fb_name)
        print('-'*50, '\n')

        counter += 1
        sleep(10 + (random()*10 - 5))

        if not counter % 45:
            sleep(15)

driver.close()
