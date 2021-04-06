'''
Created on 06.04.2021

@author: wf
'''
import glob
from os.path import expanduser

class PageFixer(object):
    '''
    helper fixing page
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def getAllPages(self):
        '''
        get all wiki pages
        '''
        home = expanduser("~")
        allPages = glob.glob('%s/wikibackup/%s/*.wiki' % (home,self.wikiId))
        return allPages
    
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
                if wikison  in event:
                    yield page,event
        