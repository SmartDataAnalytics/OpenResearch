'''
Created on 13.07.2021

@author: wf
'''
from ormigrate.fixer import PageFixer

class NullValueFixer(PageFixer):
    '''
    Fixer for https://github.com/SmartDataAnalytics/OpenResearch/issues/150
    '''

    def __init__(self, wikiFileManager):
        '''
        Constructor
        '''
        super(NullValueFixer, self).__init__(wikiFileManager)
        
if __name__ == '__main__':
    PageFixer.cmdLine([NullValueFixer])