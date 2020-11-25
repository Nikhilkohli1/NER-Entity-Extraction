
import boto3
from boto3.dynamodb.conditions import Key, Attr
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from time import sleep
import re
from selenium.webdriver.chrome.options import Options
import time

#driver = webdriver.Chrome(executable_path='chromedriver.exe')

region = 'us-east-1'
s3_client = boto3.resource('s3', region_name = region)


def open_browser(alt_user_name = 'Thank you for your website'):
    opts = Options()
    opts.add_argument("user-agent=" + str(alt_user_name))
    path = 'chromedriver.exe'
    return webdriver.Chrome(executable_path = path, options=opts)

#url = 'https://seekingalpha.com/article/4390476-ford-motor-company-f-management-presents-barclays-2020-global-automotive-conference'
def scrape_earnings(url):
	path = '/usr/bin/chromedriver'

	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('--disable-gpu')
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--ignore-certificate-errors')
    
	browser = webdriver.Chrome(executable_path = path, options=chrome_options)
	browser.get(url)
	soup    = BeautifulSoup(browser.page_source, 'html.parser')
	article = soup.find('article')
	text_ = [item.text for 
			item in article.find_all('p')]
	text_ = text_[:15]
	browser.close()
	timestr = time.strftime("%Y%m%d-%H%M%S")
	file_name = 'earnings_transcript_' + timestr + '.txt'
	#print timestr
	with open(file_name, 'w', encoding='utf8') as transcript:
		for text in text_:

			transcript.write(text)
			transcript.write('\n')
	transcript.close()

	return file_name


def scrape_transcripts(url : str):
	file_ = scrape_earnings(url)
	response = s3_client.Object('ner-recognized-entites','scraper_output/{}'.format(file_)).upload_file(Filename=file_)
	
	return file_
