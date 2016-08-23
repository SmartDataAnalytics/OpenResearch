import os
import requests
from bs4 import BeautifulSoup


class Crawler:

    def __init__(self, login_username, login_password, login_url='http://mwcsvimport.pronique.com/users/login'):
        self.username = login_username
        self.password = login_password
        self.credentials = {'data[User][username]': self.username, 'data[User][password]': self.password}
        self.loginpage = login_url
        self.session = ''

    def login(self):
        self.session = requests.Session()
        try:
            response = self.session.post(self.loginpage, data=self.credentials)
            print 'Login successfully!'
        except Exception, e:
            print e.message
        if response.status_code != 200:
            print "Can't connect to http://mwcsvimport.pronique.com/users/login, (status code: " + response.status_code \
                  + ")"

    def upload_csv(self, path):
        file = {'data[Dataset][csvfile]': ('events0.csv', open('./events/events0.csv', 'rb'), 'text/csv')}
        url = 'http://mwcsvimport.pronique.com/datasets/add'
        values = {'upload_type': 'standard', 'upload_to': '0'}
        r = self.session.post(url, files=file)
        print r.headers
        print r.request.headers
        #all_files = []
        #for subdir, dirs, files in os.walk(path):
        #    for file in files:
        #        all_files.append(open(subdir + os.sep + file, "rb"))
        #self.session.post('http://mwcsvimport.pronique.com/datasets/add', data={}, files={'data[Dataset][csvfile]': all_files[0]})
        #print 'uploading: ' + subdir + os.sep + file
        #myfile = {'file': open(subdir + os.sep + file, 'rb')}
        #upload = self.session.post('http://mwcsvimport.pronique.com/datasets/add', data={}, files={'data[Dataset][csvfile]': myFile})
        #print self.session.headers
        #myFile.close()

    def delete_csv(self):
        # delete csv data from mediawiki csv import
        base = 'http://mwcsvimport.pronique.com/'
        page = 'http://mwcsvimport.pronique.com/datasets/index/page:'

        page_number, total_pages = 1, 1
        more_data = True
        del_urls = []
        while more_data and page_number <= total_pages:
            try:
                data = self.session.get(page + str(page_number))
                print 'get page: ' + str(page_number)
            except Exception, e:
                more_data = False
                print e.message
            if data.status_code != 200:
                print "There are no more files to delete (status code: " + data.status_code + ")"

            soup = BeautifulSoup(data.text, "html.parser")

            if page_number == 1:
                for pages in soup.find_all('p', attrs={'class': 'paging-status'}):
                    total_pages = int(pages.text.split(', ')[0].split(' ')[-1])

            for table in soup.body.find_all('table', attrs={'cellpadding': '0'}):
                for tr in table.find_all('tr'):
                    for td in tr.find_all('td', attrs={'class': ""}):
                        for href in td.find_all('a', href=True):
                            if 'delete' in href['href']:
                                del_urls.append(base + href['href'])
                                print del_urls[-1]

            page_number += 1

        print 'Start to delete files'
        for url in del_urls:
            print 'delete: ' + url
            r = self.session.get(url)


crawler = Crawler('username', 'password')
crawler.login()
crawler.upload_csv('./events')
# crawler.delete_csv()



