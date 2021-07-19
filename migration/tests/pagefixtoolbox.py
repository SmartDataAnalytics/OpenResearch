'''
Created on 2021-07-14

@author: wf
'''
import os
from ormigrate.fixer import PageFixerManager
from tests.corpusfortesting import CorpusForTesting as Corpus
from ormigrate.toolbox import Profiler

class PageFixerToolbox(object):
    '''
    support default Pagefixer setup for testing
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    @staticmethod
    def getPageFixer(pageFixerClass,debug=False):
        '''
        get a page fixer for the given pageFixerClass
        '''
        wikiFileManager=Corpus.getWikiFileManager()
        pageFixerManager=PageFixerManager([pageFixerClass],wikiFileManager,debug=debug)
        fixer=pageFixerClass(pageFixerManager)
        return fixer
        pass
    
    def getRatingCounters(self,pageTitleList:list,pageFixerClass,template="Event",debug=True):
        '''
        get the rating counters for the given pageFixerClass and template
        
        Args:
            pageTitleList(list): a list of pageTitles - if None will be replaced by a list of all pages
            pageFixerClass(): the class of the pageFixer to be instantiated and tested
            template(str): the template to filter the WikiSon entities
            debug(bool): if True show the pain Counters
        Returns:
            the rating/pain counters as per the given pageTitleList 
        '''
        pageCount="all" if pageTitleList is None else len(pageTitleList)
        profile=Profiler(f"{pageFixerClass.purpose} for {pageCount} pages")
        args=PageFixerToolbox.getArgs(pageTitleList,["--stats"],template=template,debug=self.debug)
        pageFixerManager=PageFixerManager.runCmdLine([pageFixerClass],args)
        profile.time()
        counters=pageFixerManager.getRatingCounters()
        painCounter=counters["pain"]
        if debug:
            print (painCounter)
        if pageTitleList is not None:
            self.assertEqual(0,len(pageFixerManager.errors))
            self.assertEqual(len(pageTitleList),len(pageFixerManager.ratings))
        return counters
        
    @staticmethod 
    def getPageTitleLists(*pageTitles,testAll:bool):
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
        if testAll:
            pageLists.append(None)
        return pageLists
        
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
        