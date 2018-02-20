import re
import random
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException


URL_STOP_WORDS = ['pages', 'profile.', 'HS', 'highschool', 'Elementary', 'Middle School', 'Middle-School', 'High School']
ENGINES = ['google']
USER_AGENTS = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36']


def start_browser():
    fp = webdriver.FirefoxProfile()
    fp.set_preference("general.useragent.override", random.choice(USER_AGENTS))
    fp.update_preferences()

    browser = webdriver.Firefox(firefox_profile=fp)
    browser.implicitly_wait(10)
    return fp, browser
    

def get_district_names(filename):
    with open(filename) as f:
        dists = f.readlines()
    return dists


def get_query(dist_name):
    d_words = dist_name.split(' ')
    # if name ends with "School District" search "Schools" instead
    if d_words[-2:] == ['School', 'District']:
        query = ' '.join(d_words[:-2]) + ' Schools Michigan facebook'
    else:
        query = dist_name + ' Michigan facebook'
    return query


def randomize_user_agent(fp):
    fp.set_preference("general.useragent.override", random.choice(USER_AGENTS))
    fp.update_preferences()


def extract_name(res):
    if res == 'NOT FOUND':
        return 'NOT FOUND'

    if len(res.split('/')) >= 4:
        fb_name = res.split('/')[3].split('?')[0]
        return fb_name

    elif len(res.split('/')) == 2:
        print('short facebook URL.')
        fb_name = res.split('/')[1].split('?')[0]
        return fb_name

    else:
        print('Facebook URL is weird:', res)
        return 'NOT FOUND'


def sort_candidates(can):
    for c in can:
        user, likes = c
        if 'district' in user or 'public' in user:
            can.remove(c)
            can.append((user, likes*10))

    return sorted(can, key=lambda tup: tup[1], reverse=True)


def find_best(res_list, e):
    url_path = {'google': './/h3[@class="r"]/a[@href]',
        'bing': './/h2/a[@href]',
        'yahoo': '//div/span[@class=" fz-ms fw-m fc-12th wr-bw lh-17"]'}[e]
    txt_path = {'google': './/div[@class="s"]/div/span[@class="st"]',
        'bing': ['//div[@class="b_caption"]/p', '//div[@class="b_caption"]/div[@class="b_snippet"]/p'],
        'yahoo': './/div[@class="compText aAbs"]/p[@class="lh-16"]'}[e]
    result_likes = []
    for l in res_list:
        try:
            if e is 'yahoo':
                url = l.find_element(By.XPATH, url_path).text
                text = l.find_element(By.XPATH, txt_path).text
            if e is 'bing':
                url = l.find_element(By.XPATH, url_path).text
                text = l.find_element(By.XPATH, txt_path[0]).text
                if not text:
                    print('gotta add b snippet')
                    text = l.find_element(By.XPATH, txt_path[1]).text
            if e is 'google':
                url = l.find_element(By.XPATH, url_path).get_attribute('href')
                text = l.find_element(By.XPATH, txt_path).text
        except StaleElementReferenceException:
            break

        print(url)
        print(text)
        # if 'schools' in url and 'facebook' in url:

        if any(w in url for w in URL_STOP_WORDS) or ('facebook' not in url) or ('likes' not in text):
            print('stopped')
            continue
        else:
            num_likes = re.findall(r'(\d+)\slikes', l.text)
            k_likes = re.findall(r'([\d\.]+)K\slikes', l.text)
            if num_likes:
                result_likes.append((url, int(num_likes[0])))
            elif k_likes:
                result_likes.append((url, int(float(k_likes[0]) * 1000)))

    sor = sort_candidates(result_likes)
    print('sorted candidates:\n', sor)
    
    if not sor:
        print('No candidates.')
        return 'NOT FOUND'

    return sor[0][0]


def get_fb_name(driver, query, e):
    engine_url = {'google': 'http://www.google.com',
        'bing': 'http://www.bing.com',
        'yahoo': 'http://search.yahoo.com'}[e]
    input_elem_name = {'google': 'q',
        'bing': 'q',
        'yahoo': 'p'}[e]
    result_locator = {'google': '//div[@class="rc"]', 
        'bing': '//li[@class="b_algo"]', 
        'yahoo': '//div[@class="dd algo algo-sr fst Sr"]'}[e]

    driver.get(engine_url)

    input_element = driver.find_element_by_name(input_elem_name)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, input_elem_name)))
    input_element.send_keys(query)
    try:
        input_element.submit()
    except StaleElementReferenceException:
        pass
    sleep(9)
    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, result_locator)))
        driver.execute_script("window.scrollTo(0, {});".format(random.random()*108))
    except TimeoutException:
        pass

    rcs = driver.find_elements(By.XPATH, result_locator)
    best_result = find_best(rcs, e)
    
    return extract_name(best_result)


def main():
    fp, driver = start_browser()
    district_names = get_district_names('dists_remain.txt')
    
    fb_names = []
    for i, dist_name in enumerate(district_names):
        engine = random.choice(ENGINES)
        query = get_query(dist_name)
        randomize_user_agent(fp)

        print('DISTRICT: ', dist_name)
        print('Engine: ', engine)

        fb_name = get_fb_name(driver, query, engine)
        fb_names.append(fb_name)
        with open('outfile2.txt', 'a') as f:
            f.write(fb_name + '\n')

        print('\nResult:', fb_name)
        print('-'*50, '\n')

        # sleep(10 + (random.random()*10 - 5))

    driver.close()
    return None

main()
