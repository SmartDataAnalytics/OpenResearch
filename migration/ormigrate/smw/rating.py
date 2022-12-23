'''
Created on 2021-04-16

@author: wf
'''
from __future__ import annotations

import typing
from collections import ChainMap
from typing import TYPE_CHECKING
from lodstorage.jsonable import JSONAbleList, JSONAble
from corpus.quality.rating import Rating, RatingType
from wikifile.wikiFile import WikiFile

if TYPE_CHECKING:
    from ormigrate.smw.pagefixer import EntityFixer

class PageRating(Rating):
    '''
    I am a Rating for a page
    '''
    
    def __init__(
            self,
            pageTitle: str = None,
            templateName: str = None,
            pain: int = -1,
            reason: RatingType = None,
            hint: str = None
    ):
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
    
    def __init__(self, entity: JSONAble, fixer: EntityFixer = None, pageTitle: str = None):
        '''
        construct me

        Args:
            entity(JSONAble): entity to be rated/fixed
            fixer(EntityFixer): fixer responsible for rating/fixing the entity
        '''
        pageTitle = getattr(entity, "pageTitle", None) if not pageTitle else pageTitle
        template_name = getattr(entity, "templateName", None)
        super().__init__(pageTitle=pageTitle, templateName=template_name)
        self.entity = entity
        self.fixer = fixer
        self.wikiFile: typing.Union[WikiFile, None] = None

    def getRecord(self):
        # ToDo: Limit to entity properties (exclude auxiliary properties)
        return self.entity.__dict__

    def getRawRecords(self):
        '''Returns the raw entity values of the wiki markup file'''
        if self.wikiFile:
            if hasattr(self.entity, "templateName"):
                templateName = self.entity.templateName
                rawRecords = self.wikiFile.extractTemplatesByName(templateName)
                if rawRecords:
                    return dict(ChainMap(*rawRecords))
        return dict()

    def rate(self):
        """uses the assigned fixer to rate itself"""
        self.fixer.rate(self)
        
class PageRatingList(JSONAbleList):
    '''
    a container for page ratings
    '''
    def __init__(self):
        '''
        construct me
        '''
        super(PageRatingList, self).__init__("pageRatings", PageRating, "pageratings")

