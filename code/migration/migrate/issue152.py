'''
Created on 2021-04-02

@author: wf
'''
import glob
from os.path import expanduser

class AcceptanceRateFixer(object):

    '''
    fixes Acceptance Rate Not calculated
    '''


    def __init__(self, wikiId="or"):
        '''
        Constructor
        '''
        self.wikiId=wikiId
        
        
    def getAllPages(self):
        home = expanduser("~")
        allPages = glob.glob('%s/wikibackup/%s/*.wiki' % (home,self.wikiId))
        return allPages
        