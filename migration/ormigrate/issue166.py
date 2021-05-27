'''
Created on 2021-04-06

@author: wf
'''
import re
from ormigrate.fixer import PageFixer
from difflib import SequenceMatcher
from ormigrate.toolbox import HelperFunctions as hf
from lodstorage.sql import SQLDB
from os.path import expanduser

class WikiCFPIDFixer(PageFixer):
    '''
    fixer for Acceptance Rate Not calculated
    https://github.com/SmartDataAnalytics/OpenResearch/issues/163
    '''

    def __init__(self, wikiClient, debug=False):
        '''
        Constructor
        '''
        # call super constructor
        super(WikiCFPIDFixer, self).__init__(wikiClient)
        self.debug = debug
        home = expanduser("~")
        dbname="%s/.ptp/Event_all.db" % home
        self.sqlDB = SQLDB(dbname=dbname)


    def getPageWithWikicfpid(self,page,event):
        pages=re.search(r'This CfP was obtained from.*\[.*http:\/\/www\.wikicfp\.com.*]',event)
        if pages is not None:
            wikicfpidsearch= re.search(r'\[.*http:\/\/www\.wikicfp\.com.*eventid=(\d*).*]',event)
            try:
                wikicfpid=wikicfpidsearch.group(1)
            except IndexError as Idx:
                return None
            return wikicfpid
        return None

    def fixPageWithDplp(self,page,event,wikicfpID):
        query = 'Select * From Event_wikicfp where wikiCFPId = %s' % wikicfpID
        dblpLOD = self.sqlDB.query(query)
        # print(page)
        orEvent = hf.wikiSontoLOD(event)[0]
        if len(dblpLOD)> 0:
            for dic in dblpLOD:
                if 'Title' in orEvent and 'Acronym' in orEvent:
                    titleMatcher= SequenceMatcher(None,dic['title'].lower(),orEvent['Title'].lower())
                    AcronymMatcher = SequenceMatcher(None, dic['acronym'].lower(), orEvent['Acronym'].lower())
                    if AcronymMatcher.ratio() > 0.5 or titleMatcher.ratio() > 0.5:
                        orEvent['WikiCFP-ID'] = wikicfpID
                        newWikiSon=hf.dicttoWikiSon(orEvent)
                        regex = r'{{ *Event(?:.|\r|\n)*\}}'
                        re_groups = re.search(regex, event)
                        fixedEvent=event.replace(re_groups.group(),newWikiSon)
                        return fixedEvent
                    return None
                else:
                    if self.debug:
                        print('Title or acronym not found')
                        print(dic)
                        print(orEvent)






if __name__ == "__main__":
    fixer = WikiCFPIDFixer()
    fixer.debug = True
    for page,event in fixer.getAllPageTitles4Topic():
        wikicfpid= fixer.getPageWithWikicfpid(page,event)
        if wikicfpid is not None:
            fixedEvent=fixer.fixPageWithDplp(page,event,wikicfpid)
            if fixedEvent is not None:
                fixer.fixFile(page,fixedEvent,'WikiCFP')


