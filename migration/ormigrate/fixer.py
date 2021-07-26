'''
Created on 21.07.2021

@author: wf
'''
from ormigrate.smw.pagefixer import EntityFixer, PageFixerManager
from openresearch.orevent import EventList, EventSeriesList

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
        self.propertyLookups["Event"]=EventList.getPropertyLookup()
        self.propertyLookups["Event series"]=EventSeriesList.getPropertyLookup()
        