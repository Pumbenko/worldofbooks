import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


def get_page_content(url):
	options = Options()
	options.headless = True
	driver = webdriver.Chrome('./chromedriver')
	driver.get(url)
	page_source = driver.page_source
	driver.quit()
	return page_source


