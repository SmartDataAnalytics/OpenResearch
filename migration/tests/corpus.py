'''
Created on 16.04.2021

@author: wf
'''
from openresearch.eventcorpus import EventCorpus
from ormigrate.toolbox import HelperFunctions as hf

class Corpus(object):
    '''
    Simplify initializing an EventCorpus for tests
    '''

    @classmethod
    def getEventCorpus(self,wikiId='or',force=False,debug=False):
        '''
        get events with series by knitting / linking the entities together
        '''
        wikiUser=hf.getSMW_WikiUser(wikiId=wikiId,save=hf.inPublicCI())
        eventCorpus=EventCorpus(debug=debug)
        eventCorpus.fromWikiUser(wikiUser,force=force)
        return eventCorpus
        