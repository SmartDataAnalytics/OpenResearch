'''
Created on 2021-04-16

@author: wf
'''
import os
from pathlib import Path

class OpenResearch(object):
    '''
    OpenResearch Infrastructur definitions
    '''

    def __init__(self):
        '''
        Constructor
        '''
    
    @staticmethod        
    def getCachePath():
        home = str(Path.home())
        cachedir="%s/.or" %home
        return cachedir
    
    @classmethod
    def getResourcePath(cls):
        path = os.path.dirname(__file__) + "/../ormigrate/resources"
        return path