import re
from time import sleep
from selenium import webdriver

delay = 1  # time to wait on each page load before reading the page

driver = webdriver.Safari()
print('Logging in...')
driver.get('http://facebook.com')
driver.find_element_by_id('email').send_keys('sashat@ispol.com')
driver.find_element_by_id('pass').send_keys('$ashmyking')
driver.find_element_by_id('loginbutton').click()
print('Login Successful!')
sleep(5)
driver.get('https://www.facebook.com/AdamsTownshipSchools/posts/')

ps = []
SCROLL_PAUSE_TIME = 0.7

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    print('scrolling....')
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

html = driver.page_source
ps = ps + re.findall(r'<abbr title="(\d{2}\/\d{2}\/\d{4}).*?".*?<\/abbr>.*?<p>(.+?)<\/p>', html)

driver.close()