import csv
import requests
import mwclient
import twitter


class Twitter:

    # get basic information defined
    def __init__(self):
        self.C_KEY = ''
        self.C_SEC = ''
        self.A_TOKEN = ''
        self.A_TOKEN_SEC = ''
        self.api = ''

    # login twitter account, and get api
    def login(self):
        self.api = twitter.Api(consumer_key=self.C_KEY,
                               consumer_secret=self.C_SEC,
                               access_token_key=self.A_TOKEN,
                               access_token_secret=self.A_TOKEN_SEC)
        return self.api

    # get a list of list ((list_name, list_members)) in twitter
    def get_lists_list(self):
        results = self.api.GetLists(screen_name='openresearch_bn')
        list_lists = []
        for list_ in results:
            members = []
            for member in self.api.GetListMembers(list_.id):
                # print member
                members.append(member.screen_name)
            list_lists.append((list_.name, members, list_.id))
        return list_lists

    # update an existing twitter list(by adding a(some) new member(s))
    def update_twitter_list(self, new_items, twitter_list, api):
        print "update twitter %s list by adding" % twitter_list[0]
        print new_items
        api.CreateListsMember(twitter_list[2], None, None, new_items) # create twitter list members

    # create a twitter list with information from category
    def create_twitter_list(self, category_list, api, site, openres):
        print 'create category: '
        print category_list
        new_list = api.CreateList(category_list[0], mode='public', description='A list of twitters related to ' + category_list[0])
        api.CreateListsMember(new_list.id, None, None, category_list[1])  # create twitter list members
        openres.update_category_page(category_list[0], new_list.screen_name, site)


class ORPage:

    def __init__(self):
        self.site = mwclient.Site(('http', 'openresearch.org'), path='/')

    def login(self):
        self.site.login('', '')

    # save the changes to a page
    def save_page(self, new_data, page):
        text = page.text()
        if new_data not in text:
            text += new_data
            page.save(text, 'append twitter feeds by robot')

    # append twittes to a wiki page if it does not exist before
    def append_page(self, account, title):
        page = self.site.pages[title]
        base = "http://openresearch.org/index.php?title="
        pre_url = '\n==Tweets by ' + title + '==\n <div><html><a class="twitter-timeline" height="400" width="350" href="https://twitter.com/'
        tweet_by = '">Tweets by '
        post_url = '</a> <script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script></html></div>'
        new_data = pre_url + account + tweet_by + account + post_url
        self.save_page(new_data, page)

    # transform the csv result to a list for a specific inline query to OpenResearch
    def get_list_from_csv(self, url):
        response = requests.get(url)
        cr = csv.reader(response.content.decode('utf-8').splitlines(), delimiter=',')
        return list(cr)

    # get a list of pages in a certain category
    def query_pages(self, op):
        url = "http://openresearch.org/Special:Ask/-5B-5BCategory:"+op+"-5D-5D-20-5B-5BHas-20twitter::%2B-5D-5D/-3FHas-20twitter%3DTwitter-20account/mainlabel%3DAcronym/limit%3D100/offset%3D0/format%3Dcsv"
        return self.get_list_from_csv(url)

    # append twittes to pages in a certain category
    def append_pages(self, pages):
        for page in pages:
            self.append_page(page[1], page[0])

    # create a twitter section on a page in category, if it does not exist
    def update_pages(self, category):
        pages = self.query_pages(category)
        self.append_pages(pages)

    """ The code bellow is for update category page """

    # get all the sub categories of "Science" from OpenResearch which contains a twitter account
    def get_category_list(self):
        url = "http://openresearch.org/Special:Ask/-5B-5BSubcategory-20of::Science-5D-5D/mainlabel%3D/limit%3D100/offset%3D0/format%3Dcsv"
        categories = self.get_list_from_csv(url)

        # for each category, if it contains pages with "Twitter" account then add to list
        categories_twitter = []
        for category in categories:
            if len(category) > 0 and 'science' not in category[0]:  # temporaly avoid encoding error in category "Computer science"
                url1 = "http://openresearch.org/Special:Ask/-5B-5B"+category[0]+"-5D-5D-20-5B-5BHas-20twitter::%2B-5D-5D/-3FHas-20twitter/mainlabel%3D/limit%3D100/offset%3D0/format%3Dcsv"
                twitters_in_category = self.get_list_from_csv(url1)
                if len(twitters_in_category) > 1:
                    categories_twitter.append((category, twitters_in_category))
        return categories_twitter

    # insert twitter code to OpenResearch page
    def update_category_page(self, title, list_name, site):
        page = site.pages[title]
        new_data = '<div id="fixbox"><html><a class="twitter-timeline" height="500" width="180" href="https://twitter.com/openresearch_bn/lists/'+list_name+'">A Twitter List by openresearch_bn</a> <script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script></html></div>'
        self.save_page(new_data, page)

    # compare category list and twitter list items, return the not added elements in twitter list
    def elements_checker(self, category_list, twitter_list):
        category_elements = [x[1].replace('@', '') for x in category_list[1]]
        print 'category'
        print category_elements[1:]
        print 'twitter list'
        print twitter_list[1]
        return list(set(category_elements[1:]).symmetric_difference(set(twitter_list[1])))

    # check whether a category twitter list appears in a twitter list or not
    def category_twitters_checker(self, category_list, twitters_list, twit, openres):
        new_items = []
        exist = 0
        category = category_list[0][0].replace('Category:', '').lower()
        print category
        for twitter_list in twitters_list:
            print twitter_list
            if category == twitter_list[0]:  # if category already exist in twitter list
                print 'Category exists in twitter already'
                exist = 1
                new_items = self.elements_checker(category_list, twitter_list)  # check whether their elements are the same or not
                break
        if exist != 1:  # if category does not exist in twitter list
            twit.create_twitter_list(category_list, twit.api, self.site, openres)
        elif len(new_items) > 0:
            twit.update_twitter_list(new_items, twitter_list, twit.api)

    # check whether the twitters in category are all included in the twitter list or not
    def validation(self, twitter_lists, categories_lists, twit, openres):
        for category_list in categories_lists:
            self.category_twitters_checker(category_list, twitter_lists, twit, openres)


openres = ORPage()
openres.login()
# openres.update_pages("Organization")

twit = Twitter()
twit.login()
lists_list = twit.get_lists_list()  # get list of ((list, members)) in twitter account
categories_list = openres.get_category_list()  # get the categories which contains twitters account
openres.validation(lists_list, categories_list, twit, openres)  # check whether lists in twitter are idental with lists in each category
