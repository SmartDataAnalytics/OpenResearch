'''
Created on 2021-04-16

@author: wf
'''
from enum import Enum

class RatingType(Enum):
    '''
    the rating type
    '''
    missing='❌'
    invalid='👎'
    ok='👍'
    
class Rating(object):
    '''
    I am rating
    '''

    def __init__(self,pain:int,reason:str,hint:str):
        '''
        Constructor
        
        Args:
            pain(int): the painLevel
            reason(str): the reason one of missing, invalid or ok
            hint(str): the description of the rating - hint on what is wrong
        '''
        self.set(pain,reason,hint)
        
    def set(self,pain:int,reason:str,hint:str):
        '''
        set my rating
        '''
        self.pain=pain
        self.reason=reason
        self.hint=hint
        
    def __str__(self):
        return f"{self.pain} - {self.reason}: {self.hint}"
        
class PageRating(Rating):
    '''
    I am a Rating for a page
    '''
    
    def __init__(self,pageTitle:str,templateName:str,pain:int,reason:str,hint:str):
        '''
        construct me
        
        Args:
            pageTitle(str): the title of the page this rating is for
            templateName(str): the name of the template/wikiSON entity
            pain(int): the painLevel
            reason(str): the reason one of missing, invalid or ok
            hint(str): the description of the rating - hint on what is wrong
        '''
        super(PageRating,self).__init__(pain,reason,hint)
        self.pageTitle=pageTitle
        self.templateName=templateName
        
