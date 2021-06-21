from dateutil import parser
import os
from ormigrate.dictionary import Dictionary
from wikibot.wikiuser import WikiUser
from wikibot.wikiclient import WikiClient
import getpass
import re

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
    def getResourcePath(cls):
        path = os.path.dirname(__file__) + "/resources"
        return path
    
    @classmethod
    def absoluteFilePaths(cls,directory):
        """
        Get all file paths in the given directory.
        """
        #https://stackoverflow.com/questions/9816816/get-absolute-paths-of-all-files-in-a-directory
        for dirpath, _, filenames in os.walk(directory):
            for f in filenames:
                yield os.path.abspath(os.path.join(dirpath, f))

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
                wikiDict={"wikiId": wikiId,"email":"noreply@nouser.com","url":"https://www.openresearch.org","scriptPath":"/mediawiki/","version":"MediaWiki 1.31.1"}
            if wikiId=="orclone":
                wikiDict={"wikiId": wikiId,"email":"noreply@nouser.com","url":"https://confident.dbis.rwth-aachen.de","scriptPath":"/or/","version":"MediaWiki 1.35.1"}
            if wikiId=="cr":
                wikiDict={"wikiId": wikiId,"email":"noreply@nouser.com","url":"https://cr.bitplan.com","scriptPath":"/","version":"MediaWiki 1.33.4"}
                
            if wikiDict is  None:
                raise Exception("wikiId %s is not known" % wikiId)
            else:    
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
    def loadDictionary(cls):
        resourcePath=HelperFunctions.getResourcePath()
        path="%s/dictionary.yaml" %resourcePath
        lookup_dict = Dictionary(path)
        return lookup_dict

    @classmethod
    def wikiSontoLOD(self, wiki_sample, entity="Event"):
        regex= '{{ *%s(?:.|\r|\n)*\}}' % entity
        re_groups=re.search(regex,wiki_sample)
        if re_groups is not None:
            property_list = re_groups.group().replace('}}', '').split('|')[1:]
            wikidict = {}
            for i in property_list:
                mapping = i.strip().split('=')
                try:
                    wikidict[mapping[0].strip()] = int(mapping[1].strip())
                except:
                    wikidict[mapping[0].strip()] = mapping[1].strip()
            return [wikidict]
        return []

    @classmethod
    def dicttoWikiSon(self, dic, entity="Event"):
        wikiSon= "{{%s\n" % entity
        for key in dic:
            wikiSon += "|%s = %s \n" %(str(key),str(dic[key]))
        wikiSon+= "}}"
        return wikiSon