'''
Created on 16.04.2021

@author: wf
'''
from datasources.openresearch import OREventCorpus, OREventManager
from lodstorage.storageconfig import StorageConfig

from ormigrate.toolbox import HelperFunctions as hf
from wikifile.wikiFileManager import WikiFileManager
from os import path
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
        config=cls.getStorageConfig()
        cachePath=config.getCachePath()
        for entityName in ["Event","EventSeries"]:
            jsonFile=f"{cachePath}/{entityName}.json"
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
        config = cls.getStorageConfig()
        eventCorpus=OREventCorpus(config,debug=debug)
        eventCorpus.fromCache(wikiUser,force=force)
        eventCorpus.wikiFileManager=cls.getWikiFileManager(wikiId, debug)
        return eventCorpus

    @classmethod
    def getEventCorpusFromWikiText(cls,wikiId=None,debug=False):
        """
        get events with series by knitting/linking entities from a WikiFileManager
        """
        if wikiId is None:
            wikiId=cls.wikiId
        config=cls.getStorageConfig()
        wikiFileManager=cls.getWikiFileManager(wikiId,debug)
        eventCorpus=OREventCorpus(config,debug=debug)
        eventCorpus.fromWikiFileManager(wikiFileManager)
        return eventCorpus

    @classmethod
    def getStorageConfig(cls):
        return StorageConfig.getSQL()
