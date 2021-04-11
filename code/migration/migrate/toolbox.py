from dateutil import parser
import os
from migrate.Dictionary import Dictionary
from pathlib import Path


class HelperFunctions:
    def __init__(self,debug):
        'Constructor'
        self.debug=False

    @classmethod
    def parseDate(self,date):
        '''
        parses the date in any format to the format YYYY/MM/DD
        Args:
            date: Given date in any format
        Returns:
            date(str): Date in YYYY/MM/DD format. None if date cannot be converted
        '''
        try:
            parseToDatetime = parser.parse(date)
        except ValueError as e:
            return None
        datetimeToDate = parseToDatetime.date()
        datetimetoString = datetimeToDate.strftime("%Y/%m/%d")
        return datetimetoString

    @classmethod
    def loadDictionary(self):
        path = os.path.dirname(__file__) + "/../../dataset/dictionary.yaml"
        lookup_dict = Dictionary(path)
        return lookup_dict

    @classmethod
    def ensureDirectoryExists(self,directory):
        '''
        Given a path ensures the directory exists. New directory will be made if it doesn't exist
        Args:
            directory(str): PAth to directory
        '''
        Path(directory).mkdir(parents=True, exist_ok=True)

    @classmethod
    def WikiSontoLOD(self, wiki_sample):
        property_list = wiki_sample.replace('}}', '').split('|')[1:]
        wikidict = {}
        for i in property_list:
            mapping = i.strip().split('=')
            try:
                wikidict[mapping[0]] = int(mapping[1])
            except:
                wikidict[mapping[0]] = mapping[1]
        return [wikidict]


    def getHomePath(localPath):
        '''
        get the given home path
        '''
        homePath=str(Path.home() / localPath)
        ensureDirectoryExists(homePath)
        return homePath