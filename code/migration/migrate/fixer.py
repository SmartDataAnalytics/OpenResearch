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
        self.debug=debug

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

    def getAllPagesFromFile(self,file=stdin):
        allx = file.readlines()
        return allx
    
    
    def getNameValue(self,element,dostrip=True,separator="="):
        '''
        get a name value pair from a wikison element like |a=b
        
        Args:
            element(str): the element to check
            strip(bool): should spaces be removed
            separator(str): the separator - default is "="
        
        Returns:
            name(str): the name
            value(str): the value
        '''
        if element.startswith("|"):
            parts = element[1:].split(separator,1)
            if len(parts)==2:
                name=parts[0]
                value=parts[1]
                if dostrip:
                    value=value.strip()
                return name,value
        return None,None
    
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

        