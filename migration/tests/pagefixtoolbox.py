'''
Created on 2021-07-14

@author: wf
'''
import os

class PageFixerToolbox(object):
    '''
    support default Pagefixer setup for testing
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
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
        