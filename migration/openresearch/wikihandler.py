'''
Created on 12.07.2021

@author: wf
'''
from lodstorage.csv import CSV
import os
import tempfile
import csv
from wikifile.wikiFileManager import WikiFileManager
from openresearch.event import EventList

class Wikihandler(object):
    '''
    handles wiki specific migration tasks
    '''

    def __init__(self, wikiId="orclone"):
        '''
        Constructor
        
        Args:
            wikiId(str): the id of the wiki this handler is responsible for
        '''
        self.wikiId=wikiId
        
        
    def importCsvToWiki(self,csv): 
        '''
        import the given csv to the wiki with the given wikiId
        
        csv(file like object): the csv file to handle
        
        '''
        with tempfile.TemporaryDirectory() as tmpdir:
            # The context manager will automatically delete this directory after this section
            print(f"Created a temporary directory: {tmpdir}")
            filepath = os.path.join(tmpdir, csv.filename)
            csv.save(filepath)
            csvStr = CSV.readFile(filepath)
            self.importCsvStrToWiki(csvStr)
            
    def importCsvStrToWiki(self,csvStr):
        '''
        import the given CSV String to the wiki
        
        csvStr: 
        '''
        csvList = csvStr.split('\n')
        csvList = list(filter(None, csvList))
        headers = csvList[0].split(',')
        LoD = CSV.fromCSV(csvStr)
        if self.debug:
            print(csvStr)
            print(headers)
            print(LoD)
            
        
    def importLodToWiki(self,LoD):
        '''
        import the given list of dicts to my wiki
        '''
        wikiFileManager = WikiFileManager(self.wikiId)
        # FIXME why is this specific to Events?
        eventList = EventList()
        eventList.fromLoD(LoD)
        # FIXME make the call of fixers configurable
        # LocationFixer(wikiclient).fixEventRecords(LoD)
        wikiFileManager.importLODtoWiki(LoD, 'Event')
        
        