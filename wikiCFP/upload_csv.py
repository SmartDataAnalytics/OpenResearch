import os
import requests
from bs4 import BeautifulSoup

# login page of mediawiki csv import
url = 'http://mwcsvimport.pronique.com/users/login'

# user name and password for mediawiki csv import
values = {'data[User][username]': 'username', 'data[User][password]': 'password'}

# get the Session
s = requests.Session()
r = s.post(url, data=values)

# start to upload csv file
'''
for subdir, dirs, files in os.walk('./events'):
    for file in files:
        myFile = open(subdir + os.sep + file, "rb")
        upload = s.post('http://mwcsvimport.pronique.com/datasets/add', data={'submit': 'Upload'}, files={'data[Dataset][csvfile]': myFile})
'''

# delete csv data from mediawiki csv import
base = 'http://mwcsvimport.pronique.com/'
page = 'http://mwcsvimport.pronique.com/datasets/index/page:'
page_number = 1
more_data = True
del_urls = []
while more_data and page_number <= 7:
    try:
        data = s.get(page + str(page_number))
    except Exception, e:
        more_data = False
        print e.message
    if data.status_code != 200:
        print "There are no more files to delete (status code: " + data.status_code + ")"
    page_number += 1

    soup = BeautifulSoup(data.text, "html.parser")
    for table in soup.body.find_all('table', attrs={'cellpadding': '0'}):
        for tr in soup.body.find_all('tr'):
            for td in soup.body.find_all('td', attrs={'class': ""}):
                for href in soup.body.find_all('a', href=True):
                    if 'delete' in href['href']:
                        del_urls.append(base+href['href'])

for url in del_urls:
    r = s.get(url)
    print url



