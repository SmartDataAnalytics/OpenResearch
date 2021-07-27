'''
Created on 21.07.2021

@author: wf
'''
from ormigrate.smw.pagefixer import EntityFixer, PageFixerManager
from datasources.openresearch import OREventList, OREventSeriesList

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
        self.propertyLookups["Event"]=OREventList.getPropertyLookup()
        self.propertyLookups["Event series"]=OREventSeriesList.getPropertyLookup()
        