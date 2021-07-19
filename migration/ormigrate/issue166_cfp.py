'''
Created on 2021-04-06

@author: wf
'''
import re
import ntpath
from ormigrate.fixer import PageFixer,PageFixerManager
from ormigrate.rating import RatingType,PageRating
from difflib import SequenceMatcher
from lodstorage.sql import SQLDB
from os.path import expanduser
from wikifile.wikiFile import WikiFile
from wikifile.wikiRender import WikiRender


class WikiCFPIDFixer(PageFixer):
    '''
    see purpose and issue
    
    '''
    purpose="fixer for getting WikiCFP id from free text"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/166"

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(WikiCFPIDFixer, self).__init__(pageFixerManager)
        home = expanduser("~")
        self.wikiRender= WikiRender()
        dbname="%s/.ptp/Event_all.db" % home
        self.sqlDB = SQLDB(dbname=dbname)


    def getWikiCFPIdFromPage(self, eventWikiText):
        """
        Get wikiCFP ID from the text of the event if available
        Args:
            eventWikiText(str): Complete text of an event
        Returns:
            wikicfpid(int): wikicfp id if found. None if not found
        """
        pages=re.search(r'This CfP was obtained from.*\[.*http:\/\/www\.wikicfp\.com.*]',eventWikiText)
        if pages is not None:
            wikicfpidsearch= re.search(r'\[.*http:\/\/www\.wikicfp\.com.*eventid=(\d*).*]',eventWikiText)
            try:
                wikicfpid=wikicfpidsearch.group(1)
            except IndexError as _idx:
                return None
            return wikicfpid
        return None

    def fixEventFileFromWiki(self,pageTitle):
        """
        Get the pageTitle from the wiki directly and run the fixer on it
        Args:
            pageTitle(str): page title of a wiki page
        Returns:
            wikiFile(WikiFile): A WikiFile object if fixer is applied, None otherwise
        """
        wikiFileManager = self.wikiFileManager
        wikiFile = wikiFileManager.getWikiFile(pageTitle)
        event = str(wikiFile.wikiText)
        wikicfpid= self.getWikiCFPIdFromPage(event)
        if wikicfpid is not None:
            values = {}
            values['wikicfpId'] = wikicfpid
            wikiFile.add_template('Event',values)
            return wikiFile
        return None

    def fixEventFile(self,path,event):
        """
            Get the path and content of .wiki file and run the fixer on it
            Args:
                path(str): path of .wiki file
                event(str): content of .wiki file
            Returns:
                wikiFile(WikiFile): A WikiFile object if fixer is applied, None otherwise
        """
        filename = ntpath.basename(path).replace('.wiki','')
        wikiFilePath = ntpath.dirname(path)
        wikicfpid= self.getWikiCFPIdFromPage(event)
        if wikicfpid is not None:
            wikiFile = WikiFile(filename,wikiFilePath,wiki_render=self.wikiRender)
            values = {}
            values['wikicfpId']=wikicfpid
            wikiFile.add_template('Event',values)
            return wikiFile
        return None



    def fixPageWithDBCrosscheck(self, path, event, wikicfpid):
        """
        fix page of Event Series with crosschecking Event_all.db from PTP
        Args:
            path(str):path of the .wiki file
            event(str): content of the .wiki file
            wikicfpid(int): wikiCFP id of the event
        Returns:
            wikiFile(WikiFile): Returns wikiFile of the event if match in DB found otherwise None.
        """
        query = 'Select * From Event_wikicfp where wikiCFPId = %s' % wikicfpid
        dblpLOD = self.sqlDB.query(query)
        filename = ntpath.basename(path).replace('.wiki', '')
        wikiFilePath = ntpath.dirname(path)
        wikiFile = WikiFile(filename, wikiFilePath, wiki_render=self.wikiRender,wikiText=event)
        orEvent = wikiFile.extract_template('Event')
        if len(dblpLOD)> 0:
            for dic in dblpLOD:
                if 'Title' in orEvent and 'Acronym' in orEvent:
                    titleMatcher= SequenceMatcher(None,dic['title'].lower(),orEvent['Title'].lower())
                    AcronymMatcher = SequenceMatcher(None, dic['acronym'].lower(), orEvent['Acronym'].lower())
                    if AcronymMatcher.ratio() > 0.5 or titleMatcher.ratio() > 0.5:
                        values = {}
                        values['wikicfpId'] = wikicfpid
                        wikiFile.add_template('Event', values)
                        return wikiFile
                    return None
                else:
                    if self.debug:
                        print('Title or acronym not found')
                        print(dic)
                        print(orEvent)
    
    def getRatingFromWikiFile(self,wikiFile:WikiFile)->PageRating:
        '''
        Args:
            wikiFile(WikiFile): the wikiFile to work on
            
        Return:
            Rating: The rating for this WikiFile
        
        '''
        # prepare rating
        eventWikiText,_eventDict,rating=self.prepareWikiFileRating(wikiFile,"Event")
        wikiCFPId=self.getWikiCFPIdFromPage(eventWikiText)
        if wikiCFPId is None:
            rating.set(1,RatingType.ok,"no legacy wikiCFP import id  found")
        else:
            rating.set(5,RatingType.invalid,f"legacy wikiCFP reference {wikiCFPId} found")
        return rating
        

if __name__ == "__main__":
    PageFixerManager.runCmdLine([WikiCFPIDFixer])
