'''
Created on 2021-07-21

@author: wf
'''
import inspect
import sys
from enum import Enum, auto

from corpus.lookup import CorpusLookup

from ormigrate.smw.pagefixer import EntityFixer, PageFixerManager
from corpus.datasources.openresearch import OREventManager, OREventSeriesManager

class Entity(Enum):
    '''
    Entities of openresearch.
    Used to specify for a fixer the domain of operation.
    '''
    EVENT=auto()
    EVENT_SERIES=auto()
    LOCATION=auto()

class ORFixer(EntityFixer):
    '''
    OpenResearch Fixer
    '''
    worksOn=[Entity.EVENT,Entity.EVENT_SERIES]

    def __init__(self,pageFixerManager:PageFixerManager,debug=False):
        '''
        constructor
        '''
        super(ORFixer,self).__init__(pageFixerManager, debug)
        # workaround as long as we can't use MetaModel information directly from the wiki
        self.propertyLookups["Event"]=OREventManager.getPropertyLookup()
        self.propertyLookups["Event series"]=OREventSeriesManager.getPropertyLookup()
        lookup=CorpusLookup(lookupIds=["orclone-backup"], configure=self.patchEventSource,debug=debug)
        lookup.load()
        self.orDataSource = lookup.getDataSource("orclone-backup")

    def patchEventSource(self, lookup: CorpusLookup):
        '''
        patches the EventManager and EventSeriesManager by adding wikiUser and WikiFileManager
        '''
        wikiFileManager = self.wikiFileManager
        for lookupId in ["orclone", "orclone-backup", "or", "or-backup"]:
            orDataSource = lookup.getDataSource(lookupId)
            if orDataSource is not None:
                if lookupId.endswith("-backup"):
                    orDataSource.eventManager.wikiFileManager = wikiFileManager
                    orDataSource.eventSeriesManager.wikiFileManager = wikiFileManager
                else:
                    orDataSource.eventManager.wikiUser = wikiFileManager.wikiUser
                    orDataSource.eventSeriesManager.wikiUser = wikiFileManager.wikiUser