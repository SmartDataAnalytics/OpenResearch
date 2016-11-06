import csv
import requests
import mwclient

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

# get all the categories from MediaWiki within Event subcategory
def get_category_list():
    pass

# get the list elements of a twitter list with "category_name" name
def get_twitter_list(category_name):
    pass

# get the twitters account in category in MediaWiki
def get_twitters_in_category():
    pass

# check whether the twitters in category are all included in the twitter list or not
def is_same(twitter_list, twitters_in_category):
    pass

# add new elements to list or create a new list for a new category
def update_twitter_list(category_name):
    pass

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


site = mwclient.Site(('http', 'openresearch.org'), path='/')
site.login(username, password)
# update_pages("Organization")
