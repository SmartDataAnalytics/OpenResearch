'''
Created on 06.04.2021

@author: wf
'''

from os import walk,path
import re
from fnmatch import filter
from sys import stdin

class PageFixer(object):
    '''
    helper fixing page
    '''

    def __init__(self,wikiId="ormk",baseUrl="https://www.openresearch.org/wiki/",debug=False):
        '''
        Constructor
        '''
        self.wikiId = wikiId
        self.baseUrl = baseUrl

    def generateLink(self,page):
        search=r".*%s/(.*)\.wiki" % self.wikiId
        replace=r"%s\1" % self.baseUrl
        alink=re.sub(search,replace,page)
        alink=alink.replace(" ","_")
        return alink
        
    def getAllPages(self):
        '''
        get all wiki pages
        '''
        home = path.expanduser("~")
        allPages = []
        for root, dirnames, filenames in walk('%s/wikibackup/%s/' % (home,self.wikiId)):
            for filename in filter(filenames, '*.wiki'):
                allPages.append(path.join(root, filename))
        return allPages

    def getAllPagesStdin(self):
        allx = stdin.readlines()
    
    def getAllPageTitles4Topic(self,topicName="Event"):
        '''
        get all pages for the given topicName
        
        Args:
            topicName(str): the topic to "query" for
            
        Returns:
            list: the list of pageTitles
        '''
        for page in self.getAllPages():
            with open(page,'r') as f:
                event =f.read()
                wikison="{{%s" % topicName
                if wikison in event:
                    yield page,event
        