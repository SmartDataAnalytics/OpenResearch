import csv
import requests
import mwclient
import twitter
import ast
import unicodecsv

C_KEY = ''
C_SEC = ''
A_TOKEN = ''
A_TOKEN_SEC = ''

# append twittes to a wiki page if it does not exist before
def append_twitter(account, title, site):
    page = site.pages[title]
    text = page.text()
    base = "http://openresearch.org/index.php?title="
    pre_url = '\n==Tweets by ' + title + '==\n <div><html><a class="twitter-timeline" height="400" width="350" href="https://twitter.com/'
    tweet_by = '">Tweets by '
    post_url = '</a> <script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script></html></div>'
    new_data = pre_url + account + tweet_by + account + post_url
    if new_data not in text:
        text += new_data
        page.save(text, 'append twitter feeds by robot')

# get the pages in a category
def query_pages(site, op):
    url = "http://openresearch.org/Special:Ask/-5B-5BCategory:"+op+"-5D-5D-20-5B-5BHas-20twitter::%2B-5D-5D/-3FHas-20twitter%3DTwitter-20account/mainlabel%3DAcronym/limit%3D100/offset%3D0/format%3Dcsv"
    response = requests.get(url)
    cr = csv.reader(response.content.decode('utf-8').splitlines(), delimiter=',')
    return list(cr)

# append twittes to pages
def append_twitters(pages, site):
    for page in pages:
        append_twitter(page[1], page[0], site)

# create a twitter section on a page if it does not exist
def update_pages(category):
    pages = query_pages(site, category)
    append_twitters(pages, site)

# transform the csv result to a list for a specific inline query to OpenResearch
def get_list_from_csv(site, url):
    response = requests.get(url)
    cr = csv.reader(response.content.decode('utf-8').splitlines(), delimiter=',')
    return list(cr)

# get all the sub categories of "Science" from OpenResearch which contains a twitter account
def get_category_list(site):
    url = "http://openresearch.org/Special:Ask/-5B-5BSubcategory-20of::Science-5D-5D/mainlabel%3D/limit%3D100/offset%3D0/format%3Dcsv"
    categories = get_list_from_csv(site, url)

    # for each category, if it contains pages with "Twitter" account then add to list
    categories_twitter = []
    for category in categories:
        if len(category) > 0 and 'science' not in category[0]: # temporaly avoid encoding error in category "Computer science"
            url1 = "http://openresearch.org/Special:Ask/-5B-5B"+category[0]+"-5D-5D-20-5B-5BHas-20twitter::%2B-5D-5D/-3FHas-20twitter/mainlabel%3D/limit%3D100/offset%3D0/format%3Dcsv"
            twitters_in_category = get_list_from_csv(site, url1)
            if len(twitters_in_category) > 1:
                categories_twitter.append((category, twitters_in_category))
    return categories_twitter

# update an existing twitter list(by adding a(some) new member(s))
def update_twitter_list(new_items, twitter_list, api):
    print "update twitter %s list by adding" % twitter_list[0]
    print new_items
    api.CreateListsMember(twitter_list[2], None, None, new_items) # create twitter list members

# insert twitter code to OpenResearch page
def update_category_page(title, list_name, site):
    page = site.pages[title]
    text = page.text()

    new_data = '<div id="fixbox"><html><a class="twitter-timeline" height="500" width="180" href="https://twitter.com/openresearch_bn/lists/'+list_name+'">A Twitter List by openresearch_bn</a> <script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script></html></div>'

    if new_data not in text:
        text += new_data
        page.save(text, 'append twitter feeds by robot')

# create a twitter list with information from category
def create_twitter_list(category_list, api, site):
    print 'create category: '
    print category_list
    new_list = api.CreateList(category_list[0], mode='public', description='A list of twitters related to ' + category_list[0])
    api.CreateListsMember(new_list.id, None, None, category_list[1]) # create twitter list members
    update_category_page(category_list[0], new_list.screen_name, site)

# compare category list and twitter list items, return the not added elements in twitter list
def elements_checker(category_list, twitter_list):
    category_elements = [x[1].replace('@', '') for x in category_list[1]]
    return list(set(category_elements[1:]).symmetric_difference(set(twitter_list[1])))

# check whether a category twitter list appears in a twitter list or not
def category_twitters_checker(category_list, twitters_list, api, site):
    new_items = []
    exist = 0
    category = category_list[0][0].replace('Category:', '').lower()
    print category
    for twitter_list in twitters_list:
        print twitter_list
        if category == twitter_list[0]: # if category already exist in twitter list
            print 'Category exists in twitter already'
            exist = 1
            new_items = elements_checker(category_list, twitter_list) # check whether their elements are the same or not
            break;
    if exist != 1: # if category does not exist in twitter list
        create_twitter_list(category_list, api, site)
    elif len(new_items) > 0:
        update_twitter_list(new_items, twitter_list, api)


# check whether the twitters in category are all included in the twitter list or not
def validation(twitter_lists, categories_lists, api, site):
    for category_list in categories_list:
        category_twitters_checker(category_list, twitter_lists, api, site)

# check for each category whether there is new twitter account
def update_category(category_name):
    twitter_list = get_twitter_list(category_name)
    twitters_in_category = get_twitters_in_category()
    # if twitter list is not same as the twitters in category, then update twitter list in twitter
    if(is_same(twitter_list, twitters_in_category) is not True):
        update_twitter_list(category_name)

# check each category in categories whether there is a new twitter account
def update_categories():
    # get a list of categories
    categories = get_categories_list()
    for category in categories:
        update_category(category)

# login to twitter account
def login_twitter():
    api = twitter.Api(consumer_key=C_KEY,
                  consumer_secret=C_SEC,
                  access_token_key=A_TOKEN,
                  access_token_secret=A_TOKEN_SEC)
    return api

# get a list of list ((list_name, list_members)) in twitter
def get_lists_list(twitter_api):
    results = twitter_api.GetLists(screen_name='openresearch_bn')
    list_lists = []
    for list_ in results:
        members = []
        for member in twitter_api.GetListMembers(list_.id):
            # print member
            members.append(member.screen_name)
        list_lists.append((list_.name, members, list_.id))
    return list_lists


site = mwclient.Site(('http', 'openresearch.org'), path='/')
site.login('', '')
# update_pages("Organization")

twitter_api = login_twitter() # login twitter, and get api object back
lists_list = get_lists_list(twitter_api) # get list of ((list, members)) in twitter account
categories_list = get_category_list(site) # get the categories which contains twitters account
validation(lists_list, categories_list, twitter_api, site) # check whether lists in twitter are idental with lists in each category
