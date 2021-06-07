import selenium_parse

import re
import requests
from bs4 import BeautifulSoup, element
import pandas as pd

class Book:

	def __init__(self,
				 book_Tag):
		self.name = book_Tag.contents[0].text
		self.link = book_Tag.find_next('a')['href']
		self.details = get_info(self.link)
		self.actual_price = self.get_book_price('actual')
		self.original_price = self.get_book_price('original')
		self.product_rating = self.get_product_rating()
		self.viewed_or_sold_per_day = self.get_viewed_per_day()
		self.product_condition = self.get_product_condition()
		self.products_sold = self.get_products_sold()
		self.postage = self.get_postage()
		self.delivery = self.get_delivery()
		self.picture = self.get_picture()
		self.category = self.get_category()
		self.ean = ''
		self.isbn = ''
		self.item_specifics = ''
		self.get_ean_and_isbn()
		self.ebay_product_number = self.get_ebay_product_number()
		self.sku = self.get_sku()
		self.about_this_product = self.get_about_this_product()

	def get_about_this_product(self):
		about_section = next(iter(self.details.find_all('div', {'class': 'prodDetailSec'})), None)
		result= about_section.text if about_section else ''
		result=re.sub(r'[\'\"]$','', result)
		return re.sub(r'\s{2,}','',result)

	def get_ebay_product_number(self):
		result = next(iter(self.details.find_all('div', {'id': 'descItemNumber'})), '')
		return result.text if result else ''

	def get_sku(self):
		iframe = next(iter(self.details.find_all('iframe', {'id': 'desc_ifr'})), None)
		if iframe:
			details_all = get_info(iframe['src'])
			details = next(iter(details_all.find_all('div', {'id': 'details'})), None)
			if details:
				details_all_contents = next(
					iter([x.contents for x in details.contents if type(x) == element.Tag and x.name == 'table']), None)
				details_row_contents = next(
					iter([x.contents for x in details_all_contents if type(x) == element.Tag and 'SKU' in x.text.upper()]),
					None)
				sku = next(
					iter([x.text for x in details_row_contents if type(x) == element.Tag and 'SKU' not in x.text.upper()]), '')
				if not self.isbn:
					details_row_contents = next(
						iter([x.contents for x in details_all_contents if type(x) == element.Tag and 'ISBN' in x.text.upper()]),
						None)
					self.isbn = next(
						iter([x.text for x in details_row_contents if type(x) == element.Tag and 'ISBN' not in x.text.upper()]),
						'')
				return sku if sku else ''
			else:
				return ''
		else:
			return ''

	def get_category(self):
		category_all_info = next(iter(self.details.find_all('ul', {'aria-label': 'Listed in category:'})), '')
		return '/'.join([re.sub(r'\n', '', x.text) for x in category_all_info.find_all('li', {'class': 'bc-w'})][:-1])

	def get_ean_and_isbn(self):
		table = next(iter(self.details.find_all('div', {'class': 'itemAttr'})), '')
		item_specifics = table.text if table else ''
		self.item_specifics=re.sub(r'\s{2,}','',item_specifics)
		rows = table.find_all('tr')
		try:
			isbn_all_info = next(iter([x for x in rows if type(x) == element.Tag and 'ISBN' in x.text.upper()]), '')
			isbn_rows = [x.text for x in isbn_all_info if type(x) == element.Tag and 'ISBN' not in x.text.upper()]
			isbn = next(iter(x for x in isbn_rows if re.search(r'\d+', x)))
			self.isbn = re.sub(r'\n', '', isbn)
		except:
			self.isbn=''
		try:
			ean_all_info = next(iter([x for x in rows if type(x) == element.Tag and 'EAN' in x.text.upper()]), '')
			ean_rows = [x.text for x in ean_all_info if type(x) == element.Tag and 'EAN' not in x.text.upper()]
			ean = next(iter(x for x in ean_rows if re.search(r'\d+', x)))
			self.ean = re.sub(r'\n', '', ean)
		except:
			self.ean=''

	def get_book_price(self, price_type):
		if price_type == 'actual':
			price_all_info = next(iter(self.details.find_all('span', {'id': 'prcIsum'})), '')
		else:
			price_all_info = next(iter(self.details.find_all('span', {'class': 'vi-originalPrice'})), '')

		price = re.search(r'\d+.?\d+', price_all_info.text) if price_all_info else ''
		return price.group() if price else '0.00'

	def get_product_rating(self):
		result = next(iter(self.details.find_all('span', {'class': 'prodreview vi-VR-prodRev'})), '')
		return result.text if result else ''

	def get_viewed_per_day(self):
		result = next(iter(self.details.find_all('span', {'style': 'font-weight:bold;'})), '')
		return result.text if result else ''

	def get_product_condition(self):
		result = next(iter(self.details.find_all('div', {'itemprop': 'itemCondition'})), '')
		return result.text if result else ''

	def get_products_sold(self):
		result = next(iter(self.details.find_all('a', {'class': 'vi-txt-underline'})), '')
		return result.text if result else ''

	def get_delivery(self):
		result = next(iter(self.details.find_all('div', {'class': 'sh-inline-div'})), '')
		return result.text if result else ''

	def get_picture(self):
		result = next(iter(self.details.find_all('div', {'id': 'PicturePanel'})), '')
		return next(iter([x['src'] for x in result.find_all('img') if 'i.ebayimg.com/images/' in x['src']]), '')

	def get_postage(self):
		cost = next(iter(self.details.find_all('span', {'id': 'fshippingCost'})), '')
		shipping_svc = next(iter(self.details.find_all('span', {'id': 'fShippingSvc'})), '')
		cost = re.search(r'\d+.?\d+', cost.text).group() if cost else ''
		shipping_svc = re.sub(r'\n|\t', '', shipping_svc.text) if shipping_svc else ''
		cost = f'{cost}, ' if cost else ''
		return f'{cost}{shipping_svc}'

	def __repr__(self):
		return self.name


def get_info(url):
	page = requests.get(url)
	soup = BeautifulSoup(page.content, 'html.parser')
	return soup


def process_books_list(soup):
	books_list = soup.find_all('h3', {'class': 'lvtitle'})
	result = []
	if books_list:
		for book in books_list:
			try:
				result.append(
					Book(book_Tag=book)
					)
			except Exception as d:
				pass
	return result


def process_categories():
	print('Please specify page to start scraping from (in case empty - will start from 1):')
	start_from = input()
	if start_from:
		page=int(start_from)
	else:
		page = 1
	text = f'Processing pages starting from {str(page)}...'
	print(text)
	available_pages = True
	while available_pages:
		soup = get_info(f'https://www.ebay.co.uk/sch/m.html?_nkw=&_armrs=1&_from=&_ssn=worldofbooks08&_pgn={page}')
		print(f'page {page} started...')
		if soup:
			all_books_list = []
			staff = process_books_list(soup)
			if staff:
				all_books_list.extend(staff)
			else:
				new_content=''
				try:
					new_content = selenium_parse.get_page_content(
						f'https://www.ebay.co.uk/sch/m.html?_nkw=&_armrs=1&_from=&_ssn=worldofbooks08&_pgn={page}')
				except:
					print('error!')
				new_soup = BeautifulSoup(new_content, 'html.parser')
				new_staff = process_books_list(new_soup)
				if new_staff:
					all_books_list.extend(new_staff)
				else:
					available_pages = False
					print(f'ended on page {page}')

			df = pd.DataFrame([x.__dict__ for x in all_books_list])
			df.drop('details', axis='columns', inplace=True)
			df.to_csv(f'temp/temp_results_{page}.csv', sep=';', index=None)
			print(f'page {page} finished!')
			page += 1

	print('ready!')

process_categories()