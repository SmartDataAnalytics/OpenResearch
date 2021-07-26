'''
Created on 2021-04-06

@author: wf
'''
import re
import ntpath
from difflib import SequenceMatcher
from lodstorage.sql import SQLDB
from os.path import expanduser,isfile
from wikifile.wikiFile import WikiFile
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer
from ormigrate.smw.rating import EntityRating,RatingType,PageRating


class WikiCFPIDFixer(ORFixer):
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
        self.sqlDB = self.getSqlDB()
        
    def getSqlDB(self):
        '''
        get the SQL Database
        
        Returns:
            SQL Database or None if it is not available
        ''' 
        home = expanduser("~")
        self.dbPath="%s/.ptp/Event_all.db" % home
        sqlDB=None
        if isfile(self.dbPath):
            sqlDB = SQLDB(dbname=self.dbPath)
        return sqlDB
    
    def databaseAvailable(self):
        '''
        check wether the database is available
        
        Returns:
            bool: True if the database is accessible
        '''
        return self.sqlDB is not None


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

    def fix(self, rating:EntityRating):
        """
        Get the entityRating object and apply the fixer on it.
        
        Args:
            entityRating(EntityRating): EntityRating object of the Event
        """
        wikiFile = rating.wikiFile
        eventRecord = rating.getRecord()
        wikiText = str(wikiFile.wikiText)
        wikicfpid= self.getWikiCFPIdFromPage(wikiText)
        if wikicfpid is not None:
            eventRecord['wikicfpId'] = wikicfpid

    def rate(self, rating: EntityRating):
        """
        Rate the rating object as per the issue 166
        Args:
            rating(EntityRating): EntityRating object of the Event
        """
        wikiFile= rating.wikiFile
        eventWikiText = str(wikiFile.wikiText)
        wikiCFPId = self.getWikiCFPIdFromPage(eventWikiText)
        if wikiCFPId is None:
            rating.set(1, RatingType.ok, "no legacy wikiCFP import id  found")
        else:
            rating.set(5, RatingType.invalid, f"legacy wikiCFP reference {wikiCFPId} found")
        return rating


    def fixPageWithDBCrosscheck(self, wikiText, wikicfpid):
        """
        fix page of Event Series with crosschecking Event_all.db from PTP
        Args:
            wikiText(str): content of the .wiki file
            wikicfpid(int): wikiCFP id of the event
        Returns:
            wikiFile(WikiFile): Returns wikiFile of the event if match in DB found otherwise None.
        """
        query = 'Select * From Event_wikicfp where wikiCFPId = %s' % wikicfpid
        dblpLOD = self.sqlDB.query(query)
        #TODO: FIXME
        #if len(dblpLOD)> 0:
        #    for dic in dblpLOD:
        #        if 'Title' in orEvent and 'Acronym' in orEvent:
        #            titleMatcher= SequenceMatcher(None,dic['title'].lower(),orEvent['Title'].lower())
        #            AcronymMatcher = SequenceMatcher(None, dic['acronym'].lower(), orEvent['Acronym'].lower())
        #            if AcronymMatcher.ratio() > 0.5 or titleMatcher.ratio() > 0.5:
        #                values = {}
        #                values['wikicfpId'] = wikicfpid
        #                wikiFile.add_template('Event', values)
        #                return wikiFile
        #            return None
        #        else:
        #            if self.debug:
        #                print('Title or acronym not found')
        #                print(dic)
        #                print(orEvent)


    #TODO Change function when architecture is implemented.
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
