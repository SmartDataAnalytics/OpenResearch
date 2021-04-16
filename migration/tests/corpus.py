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
    def getEventCorpus(self,debug=False):
        '''
        get events with series by knitting / linking the entities together
        '''
        wikiUser=hf.getSMW_WikiUser(save=hf.inPublicCI())
        eventCorpus=EventCorpus(debug=debug)
        eventCorpus.fromWikiUser(wikiUser)
        return eventCorpus
        