'''
Created on 2021-04-06

@author: wf
'''
import re
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer, Entity
from ormigrate.smw.rating import EntityRating,RatingType

class WikiCFPIDFixer(ORFixer):
    '''
    see purpose and issue
    
    '''
    purpose="fixer for getting WikiCFP id from free text"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/166"

    worksOn = [Entity.EVENT]

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(WikiCFPIDFixer, self).__init__(pageFixerManager)

    @staticmethod
    def getWikiCFPIdFromPage(eventWikiText:str) -> int:
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
            return int(wikicfpid)
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
        wikicfpid = self.getWikiCFPIdFromPage(wikiText)
        if wikicfpid is not None:
            eventRecord['wikicfpId'] = wikicfpid

    def rate(self, rating: EntityRating):
        """
        Rate the rating object as per the issue 166
        Args:
            rating(EntityRating): EntityRating object of the Event
        """
        if getattr(rating.entity, "wikicfpId", None):
            # entity has wikicfpId correctly set
            rating.set(1, RatingType.ok, "wikicfpId is correctly set")
        else:
            wikiFile= rating.wikiFile
            eventWikiText = str(wikiFile.wikiText)
            wikiCFPId = self.getWikiCFPIdFromPage(eventWikiText)
            if wikiCFPId is None:
                rating.set(3, RatingType.missing, "no legacy wikiCFP import id  found")
            else:
                rating.set(5, RatingType.invalid, f"legacy wikiCFP reference {wikiCFPId} found")
        return rating


if __name__ == "__main__":
    PageFixerManager.runCmdLine([WikiCFPIDFixer])
