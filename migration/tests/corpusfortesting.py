'''
Created on 16.04.2021

@author: wf
'''
from openresearch.eventcorpus import EventCorpus
from ormigrate.toolbox import HelperFunctions as hf
from wikifile.wikiFileManager import WikiFileManager
from os import path
from openresearch.event import OREntityList
import os
class CorpusForTesting(object):
    '''
    Simplify initializing an EventCorpus for tests (singleton)
    '''

    wikiId='orclone'
    
    
    @classmethod
    def hasCache(cls):
        '''
        check whether the cache is available
        '''
        hasCache=True
        for entityName in ["Event","EventSeries"]:
            jsonFile=OREntityList.getJsonFile(entityName)
            hasCache=hasCache and os.path.isfile(jsonFile)
        return hasCache
    
    @classmethod
    def getWikiUser(cls,wikiId=None):
        if wikiId is None:
            wikiId= cls.wikiId
        # make sure there is a wikiUser (even in public CI)
        wikiUser=hf.getSMW_WikiUser(wikiId=wikiId,save=hf.inPublicCI())
        return wikiUser
        
    @classmethod
    def getWikiFileManager(cls,wikiId=None,debug=False):
        wikiUser=cls.getWikiUser(wikiId)
        home = path.expanduser("~")
        wikiTextPath = f"{home}/.or/wikibackup/{wikiUser.wikiId}"
        wikiFileManager = WikiFileManager(wikiId,wikiTextPath,login=False,debug=debug)
        return wikiFileManager

    @classmethod
    def getEventCorpusFromWikiAPI(cls, wikiId=None, force=False, debug=False):
        '''
        get events with series by knitting / linking the entities together
        '''
        wikiUser=cls.getWikiUser(wikiId)
        eventCorpus=EventCorpus(debug=debug)
        eventCorpus.fromWikiUser(wikiUser,force=force)
        eventCorpus.wikiFileManager=cls.getWikiFileManager(wikiId, debug)
        return eventCorpus

    @classmethod
    def getEventCorpusFromWikiText(cls,wikiId=None,debug=False):
        """
        get events with series by knitting/linking entities from a WikiFileManager
        """
        if wikiId is None:
            wikiId=cls.wikiId
        wikiFileManager=cls.getWikiFileManager(wikiId,debug)
        eventCorpus= EventCorpus(debug=debug)
        eventCorpus.fromWikiFileManager(wikiFileManager)
        return eventCorpus
