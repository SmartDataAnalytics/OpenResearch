#!/usr/bin/python
"""
This program can be used to extract semantic property with corresponding values for events in WikiCFP
run by using command from terminal: "python crawlWikiCFP.py", output will be in current directory named "events.csv"
Author: Yakun Li, Email: liyakun127@gmail.com

You can combine output of this script with http://openresearch.org/OpenResearch:HowTo to create to import multiple
events, by using the template.txt in current directory.
"""
import requests
import csv
from bs4 import BeautifulSoup

# Extract the Data
events = []


# parsing single event page in wikiCFP
def page_analysis(page_):
    dict_ = {}
    soup = BeautifulSoup(page_.text, "html.parser")
    for content in soup.body.find_all('div', attrs={'class': 'contsec'}):
        for table in content.find_all('tr'):
            for infos in table.find_all('td', attrs={'align': 'center'}):
                for info in infos.find_all('h2'):
                    for span in info.find_all('span', attrs={'property': ['v:summary', 'v:eventType', 'v:startDate',
                                                                          'v:endDate', 'v:locality', 'v:description']}):
                        if span['property'] == "v:description":
                            dict_['Title'] = span.text.encode('utf-8').strip()
                        elif span['property'] == "v:summary":
                            dict_['Acronym'] = span['content'].encode('utf-8').strip()
                        elif span['property'] == "v:startDate":
                            dict_['startDate'] = span['content']
                        elif span['property'] == "v:endDate":
                            dict_['endDate'] = span['content']
                        elif span['property'] == "v:eventType":
                            dict_['Type'] = span['content'].encode('utf-8')
                        elif span['property'] == 'v:locality':
                            location = span['content'].encode('utf-8').strip()
                            locations = [loc.strip() for loc in location.split(',')]
                            if len(locations) == 1:  # if location only contain one place, default use city
                                dict_['City'] = locations[0]
                            # if location contains more than or equal to two places, last two places are always
                            else:   # city and country
                                dict_['City'] = locations[-2]
                                dict_['Country'] = locations[-1]
                        else:
                            raise ValueError("Property not found!")

                for info in infos.find_all('a', attrs={'target': "_newtab"}):   # home page
                    dict_['Homepage'] = info['href'].encode('utf-8').strip().replace("http://", "").replace("https://",
                                                                                                            "")

                for info in infos.find_all('table', attrs={'align': "center"}):
                    for tr in info.find_all('tr'):
                        for td in tr.find_all('td', attrs={'align':"center"}):
                            for tb in td.find_all('table', attrs={'class': "gglu"}):
                                for tr_ in tb.find_all('tr', attrs={'bgcolor': ['#e6e6e6', '#f6f6f6']}):
                                    for td_ in tr_.find_all('td', attrs={'align': "center"}):
                                        proper = ''
                                        # find all the important dates
                                        for span in td_.find_all('span', attrs={'property': ['v:startDate',
                                                                                             'v:summary']}):
                                            if span['property'] == 'v:summary':  # get the key of important dates
                                                proper = span['content'].encode('utf-8')
                                            elif span['property'] == 'v:startDate':  # get the value of important dates
                                                dict_[proper] = span['content'].encode('utf-8')
                                            else:
                                                raise ValueError("Property not found!")

                                        for h5 in td.find_all('h5'):    # find all the categories
                                            category = ''
                                            for index, link in enumerate(h5.find_all('a')):
                                                if index is not 0:
                                                    category += link.text
                                                    category += ', '

                                            dict_['Field'] = category.rstrip(', ').encode('utf-8')
    events.append(dict_)


def main():
    num_pages = 10   # define how many pages to process at http://www.wikicfp.com/cfp/allcfp
    print('Extracting the data from WikiCFP')
    url = 'http://www.wikicfp.com/cfp/allcfp'
    site = 0
    more_data = True
    while more_data and site < num_pages:
        site += 1
        try:
            print 'Requesting http://www.wikicfp.com/cfp/allcfp?page=%i' % site
            data = requests.get(url, params={'page': site})
        except Exception, e:
            more_data = False
            print e.message
        if data.status_code != 200:
            print "Can't connect to WikiCFP! (status code: " + data.status_code + ")"

        # get the page
        soup = BeautifulSoup(data.text, "html.parser")
        # start to parse all the page links on current page
        for content in soup.body.find_all('div', attrs={'class': 'contsec'}):
            for table in content.find_all('tr', attrs={'bgcolor': ['#f6f6f6', '#e6e6e6']}):
                for infos in table.find_all('td', attrs={'align': 'left'}):
                    for info in infos.find_all('a'):
                        page = requests.get('http://www.wikicfp.com' + info['href'])
                        print "Processing event: http://www.wikicfp.com" + info['href']
                        page_analysis(page)

    #  write dicts to file
    all_keys = set().union(*(dict_.keys() for dict_ in events))  # union all keys from events
    #  split list into equal size 10 events in each file 
    all_events = zip(*[iter(events)]*10)
    for index, item in enumerate(all_events):
        with open("./events/events" + str(index) + ".csv", 'wb') as f:
            dict_writer = csv.DictWriter(f, all_keys)
            dict_writer.writeheader()
            dict_writer.writerows(item)


if __name__ == "__main__":
    main()
