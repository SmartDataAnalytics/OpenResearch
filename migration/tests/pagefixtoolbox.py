'''
Created on 2021-07-14

@author: wf
'''
import os

from lodstorage.jsonable import JSONAble
from wikifile.wikiFile import WikiFile
from ormigrate.smw.pagefixer import PageFixerManager, PageFixer
from ormigrate.smw.rating import EntityRating
from tests.corpusfortesting import CorpusForTesting as Corpus
from ormigrate.toolbox import Profiler
from tests.basetest import ORMigrationTest


class PageFixerToolbox(object):
    '''
    support default Pagefixer setup for testing
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    @staticmethod
    def getPageFixer(pageFixerClass,debug=False,forceUpdate:bool=False):
        '''
        get a page fixer for the given pageFixerClass
        '''
        wikiFileManager=Corpus.getWikiFileManager()
        pageFixerManager=PageFixerManager([pageFixerClass],wikiFileManager,debug=debug,forceUpdate=forceUpdate)
        fixer=pageFixerClass(pageFixerManager)
        return fixer
        pass
    
    @staticmethod
    def runAndGetPageFixerManager(testCase,pageTitleList:list,pageFixerClass,template="Event"):
        '''
        run and get a PageFixreManager for the given arguments
    
        Args:
            testCase(TestCase): a test Case for which this function is called
            pageTitleList(list): a list of pageTitles - if None will be replaced by a list of all pages
            pageFixerClass(): the class of the pageFixer to be instantiated and tested
            template(str): the template to filter the WikiSon entities
            debug(bool): if True show the pain Counters
        Returns:
            PageFixerManager: a PageFixerManager with pageRatings already set
        '''
        pageCount = "all" if pageTitleList is None else len(pageTitleList)
        profile = Profiler(f"{pageFixerClass.purpose} for {pageCount} pages")
        argv = PageFixerToolbox.getArgs(
                pageTitleList,
                ["--stats", "--ccId", "orclone-backup"],
                template=template,
                debug=testCase.debug
        )
        pageFixerManager = PageFixerManager.fromCommandLine([pageFixerClass],argv)
        wikifiles = pageFixerManager.wikiFileManager.getAllWikiFilesForArgs(pageFixerManager.args)
        pageFixerManager.wikiFilesToWorkon = wikifiles
        pageFixerManager.getRatings(debug=testCase.debug)
        profile.time()
        return pageFixerManager
    
    @staticmethod
    def getRatingCounters(testCase,pageTitleList:list,pageFixerClass,template="Event"):
        '''
        get the rating counters for the given pageFixerClass and template
        
        Args:
            testCase(TestCase): a test Case for which this function is called
            pageTitleList(list): a list of pageTitles - if None will be replaced by a list of all pages
            pageFixerClass(): the class of the pageFixer to be instantiated and tested
            template(str): the template to filter the WikiSon entities
            debug(bool): if True show the pain Counters
        Returns:
            the rating/pain counters as per the given pageTitleList 
        '''
        pageFixerManager = PageFixerToolbox.runAndGetPageFixerManager(testCase, pageTitleList, pageFixerClass, template)
        counters = pageFixerManager.getRatingCounters()
        painCounter = counters["pain"]
        if testCase.debug:
            print(painCounter)
        if pageTitleList is not None:
            testCase.assertEqual(len(pageTitleList), len(pageFixerManager.ratings))
        return counters
        
    @staticmethod
    def getArgs(pageTitles,moreArgs=None,template="Event",verbose=True,debug=False):
        '''
        get the arguments for the given pageTitles
        '''
        wikiId="orclone"
        args=[]
        if verbose:
            args.append("--verbose")
        home = os.path.expanduser("~")
        if pageTitles:
            args.append("--pages")
            for pageTitle in pageTitles:
                args.append(pageTitle)
        args.append("--source")
        args.append(wikiId)
        args.append("--wikiTextPath")
        wikiTextPath=f"{home}/.or/wikibackup/{wikiId}"
        args.append(wikiTextPath)
        if template is not None:
            args.append("--template")
            args.append(template)
        if moreArgs:
            args.extend(moreArgs)
        if debug:
            print(args)
        return args

    @staticmethod
    def getEntityRatingForRecord(record:dict):
        '''
        creates EntityRating for given record
        '''
        entity = JSONAble()
        entity.__dict__.update(record)
        entityRating = EntityRating(entity)
        return entityRating


class PageFixerTest(ORMigrationTest):
    '''
    test for pageFixer
    '''
    
    def setUp(self, debug:bool=False, profile:bool=True):
        super().setUp(debug=debug, profile=profile)
        self.testAll = True
        self.template = "Event"
        self.wikiUser = Corpus.getWikiUser()
        pass

    def getRatingCounters(self,pageTitleList:list):
        counters = PageFixerToolbox.getRatingCounters(self, pageTitleList, self.pageFixerClass, self.template)
        return counters
    
    def getPageFixer(self, forceUpdate:bool=False) -> PageFixer:
        """
        Creates the PageFixer object of the test
        Args:
            forceUpdate: If True update the ConferenceCorpus cache

        Returns:
            PageFixer
        """
        pageFixer=PageFixerToolbox.getPageFixer(self.pageFixerClass, self.debug, forceUpdate)
        return pageFixer

    def getPageTitleLists(self,*pageTitles):
        '''
        get the pageTitle lists to be tested
        
        Args:
            testAll(bool): if True add a None list entry which will initiate to test all Pages
            pageTitles(args): the pageTitles as a variable parameter argument list
        '''
        pageList=[]
        for pageTitle in pageTitles:
            pageList.append(pageTitle)
        pageLists=[pageList]
        if self.testAll:
            pageLists.append(None)
        return pageLists

    def getEntityRatingFromDict(self, records:dict, wikiText:str=None, wikiFile:WikiFile=None):
        """
        Args:
            records(dict): records of the entity
            wikiText(str): wikiMarkup content of the page
            wikiFile(str): wikiFile of the page. Has higher priority than wikiText and thus will overwrite given wikiText

        Returns:
             a EntityRating for the given dict
        """
        entity = JSONAble()
        entity.fromDict(records)
        wikiFile = None
        if wikiText is not None and wikiFile is None:
            wikiFile = WikiFile(records.get("pageTitle", "TestPage"), wikiText=wikiText)
        rating = EntityRating(entity=entity)
        rating.wikiFile = wikiFile
        return rating

    def getRecordOfEntity(self, entity:EntityRating) -> dict:
        """
        removes auxiliary properties from the entity
        Args:
            entity: EntityRating

        Returns:
            dict
        """
        return {k:v for k,v in entity.getRecord().items() if k != "smwHandler"}
        