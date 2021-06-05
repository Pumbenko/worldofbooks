from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def get_page_content(url):
	driver = webdriver.Chrome(ChromeDriverManager().install())
	driver.get(url)
	page_source = driver.page_source
	driver.quit()
	return page_source

