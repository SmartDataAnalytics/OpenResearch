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
    def getArgs(pageTitles,moreArgs=None,verbose=True,debug=False):
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
        if moreArgs:
            args.extend(moreArgs)
        if debug:
            print(args)
        return args
        