'''
Created on 16.04.2021

@author: wf
'''
from corpus.eventcorpus import EventDataSource
from corpus.lookup import CorpusLookup
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
    def getEventCorpusFromWikiAPI(cls, lookupId:str="orclone", forceUpdate:bool=False, debug:bool=False):
        '''
        get events with series by knitting / linking the entities together

        Args:
            lookupId(str): ID of the EventDataSource that should be returned.
            forceUpdate(bool): True if the data should be fetched from the source instead of the cache
            debug(bool): If True display debug output

        Returns:
            EventDataSource
        '''
        eventDataSource=cls.getEventDataSource(lookupId=lookupId, forceUpdate=forceUpdate, debug=debug)
        return eventDataSource

    @classmethod
    def getEventCorpusFromWikiText(cls, lookupId:str="orclone-backup", forceUpdate:bool=False, debug=False):
        """
        get events with series by knitting/linking entities from a WikiFileManager

        Args:
            lookupId(str): ID of the EventDataSource that should be returned.
            forceUpdate(bool): True if the data should be fetched from the source instead of the cache
            debug(bool): If True display debug output

        Returns:
            EventDataSource
        """
        eventDataSource = cls.getEventDataSource(lookupId=lookupId, forceUpdate=forceUpdate, debug=debug)
        return eventDataSource

    @classmethod
    def getEventDataSource(cls, lookupId:str, forceUpdate:bool=False, debug:bool=False):
        """

        Args:
            lookupId(str): ID of the EventDataSource that should be returned.
            forceUpdate(bool): True if the data should be fetched from the source instead of the cache
            debug(bool): If True display debug output

        Returns:
            EventDataSource
        """
        lookup = CorpusLookup(lookupIds=[lookupId], configure=cls.patchEventSource, debug=debug)
        lookup.load(forceUpdate=forceUpdate)
        eventDataSource = lookup.getDataSource(lookupId)
        return eventDataSource

    @classmethod
    def patchEventSource(cls, lookup:CorpusLookup):
        '''
        patches the EventManager and EventSeriesManager by adding wikiUser and WikiFileManager
        '''
        wikiUser = cls.getWikiUser(cls.wikiId)
        wikiFileManager = cls.getWikiFileManager(cls.wikiId)
        for lookupId in ["orclone", "orclone-backup", "or", "or-backup"]:
            orDataSource = lookup.getDataSource(lookupId)
            if orDataSource is not None:
                if lookupId.endswith("-backup"):
                    orDataSource.eventManager.wikiFileManager = wikiFileManager
                    orDataSource.eventSeriesManager.wikiFileManager = wikiFileManager
                else:
                    orDataSource.eventManager.wikiUser = wikiUser
                    orDataSource.eventSeriesManager.wikiUser = wikiUser

    @classmethod
    def getStorageConfig(cls):
        return StorageConfig.getSQL()
