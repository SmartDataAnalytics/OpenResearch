import os
from ormigrate.dictionary import Dictionary
from wikibot.wikiuser import WikiUser
from wikibot.wikiclient import WikiClient
import getpass
import time

class Profiler:
    '''
    simple profiler
    '''
    def __init__(self,msg,profile=True):
        '''
        construct me with the given msg and profile active flag
        
        Args:
            msg(str): the message to show if profiling is active
            profile(bool): True if messages should be shown
        '''
        self.msg=msg
        self.profile=profile
        self.starttime=time.time()
        if profile:
            print(f"Starting {msg} ...")
    
    def time(self,extraMsg=""):
        '''
        time the action and print if profile is active
        '''
        elapsed=time.time()-self.starttime
        if self.profile:
            print(f"{self.msg}{extraMsg} took {elapsed:5.1f} s")
        
        
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
    def ensureDirectoryExists(cls,file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

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
    def loadDictionary(cls):
        resourcePath=HelperFunctions.getResourcePath()
        path="%s/dictionary.yaml" %resourcePath
        lookup_dict = Dictionary(path)
        return lookup_dict