'''
Created on 2021-04-02

@author: wf
'''
import glob
from os.path import expanduser
import re

class AcceptanceRateFixer(object):

    '''
    fixer for Acceptance Rate Not calculated
    https://github.com/SmartDataAnalytics/OpenResearch/issues/152
    '''

    def __init__(self, wikiId="or",baseUrl="https://www.openresearch.org/wiki/",debug=False):
        '''
        Constructor
        '''
        self.wikiId=wikiId
        self.baseUrl=baseUrl
        self.debug=debug
        self.nosub=0
        self.noacc=0
        
        
    def getAllPages(self):
        '''
        get all wiki pages
        '''
        home = expanduser("~")
        allPages = glob.glob('%s/wikibackup/%s/*.wiki' % (home,self.wikiId))
        return allPages
    
    def getAllEvents(self):
        for page in self.getAllPages():
            with open(page,'r') as f:
                event =f.read()
                if "{{Event" in event:
                    yield page,event
                    
    def link(self,page):
        search=r".*%s/(.*)\.wiki" % self.wikiId
        replace=r"%s\1" % self.baseUrl
        alink=re.sub(search,replace,page)
        alink=alink.replace(" ","_")
        return alink
    

    def check(self,page,event):
        '''
        check the given page and event
        '''
        if event.lower().find('|Submitted papers='.lower()) == -1 and event.lower().find('|Accepted papers='.lower()) != -1:
            self.nosub+=1
            if self.debug: print(self.link(page))
        elif event.lower().find('|Submitted papers='.lower()) != -1 and event.lower().find('|Accepted papers='.lower()) == -1:
            if self.debug: print(self.link(page))
            self.noacc+=1
            
    def checkAll(self):
        '''
        check all events
        '''
        for page,event in self.getAllEvents():
            self.check(page,event)
            
    def result(self):
        text="submitted papers missing for %d: accepted papers missing for: %d" % (self.nosub, self.noacc)
        return text


        
if __name__ == "__main__":
    fixer=AcceptanceRateFixer()
    fixer.debug=True
    fixer.checkAll()
    print (fixer.result())
    