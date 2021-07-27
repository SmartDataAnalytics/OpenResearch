'''
Created on 2021-04-16

@author: wf
'''
from enum import Enum
from smw.topic import SMWEntity
from lodstorage.jsonable import JSONAble,JSONAbleList


class RatingType(str,Enum):
    '''
    the rating type
    
    see https://stackoverflow.com/a/51976841/1497139 why we use str as a type for better json Encoding
    '''
    missing='❌'
    invalid='👎'
    ok='👍'
    
class Rating(JSONAble):
    '''
    I am rating
    '''

    def __init__(self,pain:int=-1,reason:str=None,hint:str=None):
        '''
        Constructor
        
        Args:
            pain(int): the painLevel
            reason(str): the reason one of missing, invalid or ok
            hint(str): the description of the rating - hint on what is wrong
        '''
        self.set(pain,reason,hint)
        
    @classmethod
    def getSamples(cls):
        samplesLOD=[{
            "pain": 1,
            "reason": RatingType.ok,
            "hint": "Dates,  Jul 13, 2008 , Jul 14, 2008 valid",
        }
        ]
        return samplesLOD
        
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
    
    def __init__(self,pageTitle:str=None,templateName:str=None,pain:int=-1,reason:str=None,hint:str=None):
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
        
    @classmethod
    def getSamples(cls):
        samplesLOD=[{
            "templateName": "Event",
            "pageTitle": "Workshop on Spatial/Temporal Reasoning 2008",
            "pain": 1,
            "reason": RatingType.ok,
            "hint": "Dates,  Jul 13, 2008 , Jul 14, 2008 valid",
        }
        ]
        return samplesLOD
        
    def __str__(self):
        return f"{self.templateName} {self.pageTitle}: {self.pain} - {self.reason}: {self.hint}"
    
class EntityRating(PageRating):
    '''
    a rating for an entity
    '''
    
    def __init__(self,entity:SMWEntity):
        '''
        construct me
        '''
        super(PageRating,self).__init__()
        self.entity=entity

    def getRecord(self):
        return self.entity.__dict__

    @property
    def wikiFile(self):
        return self.entity.wikiFile
        
class PageRatingList(JSONAbleList):
    '''
    a container for page ratings
    '''
    def __init__(self):
        '''
        construct me
        '''
        super(PageRatingList, self).__init__("pageRatings", PageRating, "pageratings")
    