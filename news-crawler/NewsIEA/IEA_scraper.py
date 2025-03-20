import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
import json
import re
from IEA_F import get_titles, get_url, scrape_and_save


#PROCESS THE URL AND MAKE THE SOUP
url = 'https://www.iea.org/news/'

IEA = requests.get(url, verify=False)

IEA_soup = BeautifulSoup(IEA.text, 'html.parser')

#GET TITLES
get_titles(IEA_soup)

#GET LINKS
get_url(IEA_soup)


# SCRAPER & SAVE
scrape_and_save(get_url(IEA_soup), "C:/Users/Z_LAME/Desktop/Crawler/Downloads/News IEA")
