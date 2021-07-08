'''
Created on 2021-04-06

@author: wf
'''
import re
import ntpath
from ormigrate.fixer import PageFixer
from difflib import SequenceMatcher
from ormigrate.toolbox import HelperFunctions as hf
from lodstorage.sql import SQLDB
from os.path import expanduser
from wikifile.wikiFile import WikiFile
from wikifile.wikiRender import WikiRender
from wikifile.wikiFileManager import WikiFileManager

class WikiCFPIDFixer(PageFixer):
    '''
    fixer for getting WikiCFP id from free text
    https://github.com/SmartDataAnalytics/OpenResearch/issues/166
    '''

    def __init__(self, wikiClient, debug=False):
        '''
        Constructor
        '''
        # call super constructor
        super(WikiCFPIDFixer, self).__init__(wikiClient)
        self.debug = debug
        home = expanduser("~")
        self.wikiRender= WikiRender()
        dbname="%s/.ptp/Event_all.db" % home
        self.sqlDB = SQLDB(dbname=dbname)


    def getWikiCFPIdFromPage(self, event):
        """
        Get wikiCFP ID from the text of the event if available
        Args:
            event(str): Complete text of an event
        Returns:
            wikicfpid(int): wikicfp id if found. None if not found
        """
        pages=re.search(r'This CfP was obtained from.*\[.*http:\/\/www\.wikicfp\.com.*]',event)
        if pages is not None:
            wikicfpidsearch= re.search(r'\[.*http:\/\/www\.wikicfp\.com.*eventid=(\d*).*]',event)
            try:
                wikicfpid=wikicfpidsearch.group(1)
            except IndexError as Idx:
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
        wikiFileManager = WikiFileManager(self.wikiId)
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






# if __name__ == "__main__":
#     wikiUser = hf.getWikiClient('ormk')
#     fixer = WikiCFPIDFixer(wikiUser)
#     fixer.debug = True
#     for page,event in fixer.getAllPageTitles4Topic():
#         wikicfpid= fixer.getWikiCFPIdFromPage(page, event)
#         if wikicfpid is not None:
#             fixedEvent=fixer.fixEventFile(page, event)
#             break;
#             #     fixer.fixFile(page,fixedEvent,'WikiCFP')


