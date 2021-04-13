from dateutil import parser
import os
from migrate.Dictionary import Dictionary
from wikibot.wikiuser import WikiUser
from wikibot.wikiclient import WikiClient
import getpass

class HelperFunctions:
    '''
    general helper functions
    
    for the OpenResearch Migration project
    '''
    def __init__(self,debug=False):
        'Constructor'
        self.debug=debug
        
    @staticmethod    
    def inPublicCI():
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in [ "travis", "runner" ];

    @classmethod
    def getSMW_WikiUser(cls,wikiId="or",save=False):
        '''
        get semantic media wiki users for SemanticMediawiki.org and openresearch.org
        '''
        iniFile=WikiUser.iniFilePath(wikiId)
        wikiUser=None
        if not os.path.isfile(iniFile):
            wikiDict=None
            if wikiId=="or":
                wikiDict={"wikiId": wikiId,"email":"webmaster@openresearch.org","url":"https://www.openresearch.org","scriptPath":"/mediawiki/","version":"MediaWiki 1.31.1"}
            if wikiDict is not None:    
                wikiUser=WikiUser.ofDict(wikiDict, lenient=True)
                if save:
                    wikiUser.save()
        else:
            wikiUser=WikiUser.ofWikiId(wikiId,lenient=True)
        return wikiUser

    @classmethod
    def getWikiClient(self,wikiId='or',save=False):
        ''' get the alternative SMW access instances for the given wiki id
        '''
        wikiuser=HelperFunctions.getSMW_WikiUser(wikiId,save=save)
        wikiclient=WikiClient.ofWikiUser(wikiuser)
        return wikiclient

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
    def getResourcePath(cls):
        path = os.path.dirname(__file__) + "/../resources/"
        return path

    @classmethod
    def loadDictionary(cls):
        resourcePath=HelperFunctions.getResourcePath()
        path="%s/dictionary.yaml" %resourcePath
        lookup_dict = Dictionary(path)
        return lookup_dict

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