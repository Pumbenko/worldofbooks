import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from sys import platform
from webdriver_manager.chrome import ChromeDriverManager

def get_page_content(url):
	# options = Options()
	# options.headless = True
	#
	# driver = webdriver.Chrome('./chromedriver_mac') if platform=='darwin' else webdriver.Chrome('./chromedriver_linux', options=options)
	driver = webdriver.Chrome(ChromeDriverManager().install())
	driver.get(url)
	page_source = driver.page_source
	driver.quit()
	return page_source

