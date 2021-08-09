'''
Created on 2021-07-21

@author: wf
'''
from ormigrate.smw.pagefixer import EntityFixer, PageFixerManager
from corpus.datasources.openresearch import OREventManager, OREventSeriesManager

class ORFixer(EntityFixer):
    '''
    OpenResearch Fixer
    '''

    def __init__(self,pageFixerManager:PageFixerManager,debug=False):
        '''
        constructor
        '''
        super(ORFixer,self).__init__(pageFixerManager, debug)
        # workaround as long as we can't use MetaModel information directly from the wiki
        self.propertyLookups["Event"]=OREventManager.getPropertyLookup()
        self.propertyLookups["Event series"]=OREventSeriesManager.getPropertyLookup()
        