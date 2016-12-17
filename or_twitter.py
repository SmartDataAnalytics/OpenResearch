import csv
import requests
import mwclient
import twitter
import json
import urllib


class Twitter:

    def __init__(self):
        """Initialize with twitter login credientials
        """
        self.C_KEY = ''
        self.C_SEC = ''
        self.A_TOKEN = ''
        self.A_TOKEN_SEC = ''
        self.api = ''

    def login(self):
        """Login twitter account, and get api"""
        self.api = twitter.Api(consumer_key=self.C_KEY,
                               consumer_secret=self.C_SEC,
                               access_token_key=self.A_TOKEN,
                               access_token_secret=self.A_TOKEN_SEC)
        return self.api

    def get_lists_list(self):
        """Get a list of list ((list_name, list_members)) in twitter"""
        results = self.api.GetLists(screen_name='openresearch_bn')
        list_lists = []
        for list_ in results:
            members = []
            for member in self.api.GetListMembers(list_.id):
                members.append(member.screen_name)
            list_lists.append((list_.name, members, list_.id))
        return list_lists

    def update_twitter_list(self, new_items, twitter_list):
        """Update an existing twitter list(by adding a(some) new member(s))

        Key arguments:
        new_items -- new items will be added to twitter list
        twitter_list -- twitter list to be updated
        api -- api of object
        """
        print "update twitter list: %s" % twitter_list[0]
        print new_items
        try:
            self.api.CreateListsMember(twitter_list[2], None, None, new_items) # create twitter list members
        except Exception as e:
            print e

    def create_twitter_list(self, category_list):
        """Create a twitter list with information from category

        Key arguments:
        category_list -- category list to be created into twitter
        """
        category = category_list[0].replace('Category:', '').lower()
        print 'Create twitter list {} with elements {}'.format(category, category_list[1])
        if len(category) < 25: # twtter list lenght restriction
            new_list = self.api.CreateList(category, mode='public', description='A list of twitters related to ' + category)
            category_elements = [x.replace('@', '') for x in category_list[1]]
            try:
                self.api.CreateListsMember(new_list.id, None, None, category_elements)  # create twitter list members
            except Exception as e:
                print e


class OpenResearch(object):

    def __init__(self, username, password):
        """Set the username and password for OpenResearch

        Key arguments:
        username -- username in OR
        password -- password in OR
        """
        self.site = mwclient.Site(('http', 'openresearch.org'), path='/')
        self.username = username
        self.password = password

    def login(self):
        """Login OpenResearch
        """
        self.site.login(self.username, self.password)

    def save_page(self, new_data, page):
        """Save changes to a page

        Key arguments:
        new_data -- new append data to current page
        page -- current page edited
        """
        text = page.text()
        if new_data not in text:
            text += new_data
            page.save(text, 'append twitter feeds by robot')

    def get_query_result(self, query_url):
        """Get query result from OpenResearch in json format

        Key arguments:
        query_url -- url of query
        """
        response = urllib.urlopen(query_url)
        try:
            data = json.load(response)
        except Exception as e:
            print e
            return None
        else:
            return data

    def get_sub_categories(self, category_name, categories):
        """Get the subcategories of a category

        Key arguments:
        category_name -- category name
        categories -- keep all the subcategories
        """
        print 'Parsing subcategories of %s' % category_name
        query_url = "http://openresearch.org/Special:Ask/-5B-5BSubcategory-20of::"+category_name+"-5D-5D/mainlabel%3D/limit%3D100/offset%3D0/format%3Djson"
        data = self.get_query_result(query_url)
        if data != None:
            subcategories = [key.replace('Category:','') for key in data['results'].keys()]
            print subcategories
            categories.extend(subcategories)
            for category in subcategories:
                self.get_sub_categories(category, categories)

    def check_twitter_account(self, subcategory_name):
        """Check whether there is a twitter account in category or not

        Key arguments:
        subcategory_name -- category to be checked
        """
        url = "http://openresearch.org/Special:Ask/-5B-5BCategory:"+subcategory_name+"-5D-5D-20-5B-5BHas-20twitter::%2B-5D-5D/-3FHas-20twitter/mainlabel%3D/limit%3D100/offset%3D0/format%3Djson"
        result = self.get_query_result(url)
        twitters_in_subcategory = []
        if result != None:
            print "Twitters in subcategory %s" % subcategory_name
            for key in result['results'].keys():
                twitters_in_subcategory.extend(result['results'][key]['printouts']['Has twitter'])
            print twitters_in_subcategory
            return twitters_in_subcategory
        return None

    def get_subcategories_list(self):
        """Get get all the sub categories of "Science" from OpenResearch which contains a twitter account
        """
        all_subcategories = []
        self.get_sub_categories('Science', all_subcategories)
        # for each category, if it contains pages with "Twitter" account then add to list
        twitters_in_subcategories = []
        for subcategory in all_subcategories:
            twitters_in_subcategory = self.check_twitter_account(subcategory)
            if twitters_in_subcategory != None:
                twitters_in_subcategories.append((subcategory, twitters_in_subcategory))
        return twitters_in_subcategories

    def elements_checker(self, category_list, twitter_list):
        """Compare category list and twitter list items, return the not added elements in twitter list

        Key arguments:
        category_list -- category list contains category and corresponding twitter accounts
        twitter_list -- twitter list, same twitter list name as category
        """
        category_elements = [x.replace('@', '') for x in category_list[1]]
        # return the elements in OpenResearch category but not in corresponding list in twitter
        return [element for element in category_elements if element not in twitter_list[1]]

    def category_twitters_checker(self, category_list, twitters_list, twit):
        """Check whether a category twitter list appears in a twitter list or not

        Key arguments:
        category_list -- contains all the categories with corresponding twitters in each category
        twitter_list -- contains all the twitter lists
        twit -- a Twitter class
        """
        exist = 0
        new_items = None
        category = category_list[0].replace('Category:', '').lower()
        for twitter_list in twitters_list:
            if category == twitter_list[0]:  # if category already exist in twitter list
                print 'Elements in category {} not in twitter list {}: '.format(category, twitter_list[0])
                exist = 1
                new_items = self.elements_checker(category_list, twitter_list)
                print new_items
                break
        if exist != 1:  # if category does not exist in twitter list
            twit.create_twitter_list(category_list)
        elif len(new_items) > 0:
            twit.update_twitter_list(new_items, twitter_list)

    def validation(self, twitter_lists, categories_lists, twit):
        """Check whether the twitters in category are all included in the twitter list or not

        Key arguments:
        category_list -- contains all the categories with corresponding twitters in each category
        twitter_list -- contains all the twitter lists
        twit -- a Twitter class
        openres -- a OpenResearch class
        """
        for category_list in categories_lists:
            self.category_twitters_checker(category_list, twitter_lists, twit)


openres = OpenResearch('username', 'password') # username and password in OpenResearch
openres.login()

twit = Twitter()
twit.login()
# get list of ((list, members)) in twitter account
lists_list = twit.get_lists_list()
# get the categories which contain twitters account
categories_list = openres.get_subcategories_list()
# check whether lists in twitter are idental with lists in each category
openres.validation(lists_list, categories_list, twit)
