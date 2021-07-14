'''
Created on 16.04.2021

@author: wf
'''
from openresearch.eventcorpus import EventCorpus
from ormigrate.toolbox import HelperFunctions as hf
from wikifile.wikiFileManager import WikiFileManager
from os import path

class CorpusForTesting(object):
    '''
    Simplify initializing an EventCorpus for tests
    '''

    wikiId='orclone'

    @classmethod
    def getWikiFileManager(cls,wikiId=None,debug=False):
        if wikiId is None:
            wikiId= cls.wikiId
        home = path.expanduser("~")
        wikiTextPath = f"{home}/.or/wikibackup/{wikiId}"
        wikiFileManager = WikiFileManager(wikiId,wikiTextPath,login=False,debug=debug)
        return wikiFileManager


    @classmethod
    def getEventCorpusFromWikiAPI(cls, wikiId=None, force=False, debug=False):
        '''
        get events with series by knitting / linking the entities together
        '''
        if wikiId is None:
            wikiId=cls.wikiId
        wikiUser=hf.getSMW_WikiUser(wikiId=wikiId,save=hf.inPublicCI())
        eventCorpus=EventCorpus(debug=debug)
        eventCorpus.fromWikiUser(wikiUser,force=force)
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
