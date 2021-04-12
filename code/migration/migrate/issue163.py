'''
Created on 2021-04-06

@author: wf
'''
import re
from migrate.fixer import PageFixer
from migrate.toolbox import HelperFunctions
from wikibot.wikipush import WikiPush

class SeriesFixer(PageFixer):
    '''
    fixer for Acceptance Rate Not calculated
    https://github.com/SmartDataAnalytics/OpenResearch/issues/163
    '''

    def __init__(self, wikiId="or", baseUrl="https://www.openresearch.org/wiki/", debug=False):
        '''
        Constructor
        '''
        # call super constructor
        super(SeriesFixer, self).__init__(wikiId, baseUrl)
        self.debug = debug


    def checkAll(self,eventQuery):
        '''
        check if any event has multiple objects in series field
        '''
        """Test if LOD is returned correctly if called from api to store to SQL"""
        wikiId = 'or'
        wikiClient = HelperFunctions.getWikiClient(HelperFunctions, wikiId)
        wikiPush = WikiPush(fromWikiId=wikiId)
        askQuery = "{{#ask:" + eventQuery + "}}"
        lod_res = wikiPush.formatQueryResult(askQuery, wikiClient, entityName="Event")
        count = 0
        for i in lod_res:
            # print(str(i['series']) + ":", str(type(i['series'])))
            if type(i['series'])==list:
                # print (i)
                count +=1
                if self.debug: print(self.generateLink(i['Event']))
        return count




if __name__ == "__main__":
    fixer = SeriesFixer()
    fixer.debug = True
    # fixer.checkAll("[[IsA::Event]]| mainlabel = Event| ?Title = title| ?Event in series = series| ?_CDAT=creation date| ?_MDAT=modification date| ?ordinal=ordinal| ?Homepage = homepage|format=table")
    print(fixer.checkAll("[[3DUI]]| mainlabel = Event| ?Title = title| ?Event in series = series| ?_CDAT=creation date| ?_MDAT=modification date| ?ordinal=ordinal| ?Homepage = homepage|format=table"))