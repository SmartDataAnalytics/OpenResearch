'''
Created on 13.07.2021

@author: wf
'''
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer
from wikifile.wikiRender import WikiFile
from ormigrate.smw.rating import PageRating, RatingType, EntityRating


class NullValueFixer(ORFixer):
    '''
    see purpose and issue
    '''
    purpose="fix invalid null values"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/150"

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(NullValueFixer, self).__init__(pageFixerManager)
        
    def rate(self, rating: EntityRating):
        wikiText=rating.wikiFile.wikiText
        if rating.getRecord() is None:
            rating.set(7,RatingType.missing,"no event record found")
        else:
            nullValues=0
            nullValues=wikiText.lower().count("::some person")
            if nullValues==0:
                rating.set(1,RatingType.ok,"no nullValue found")
            elif (nullValues==1):
                rating.set(3,RatingType.invalid,"found an improper nullValue")
            else:
                rating.set(5,RatingType.invalid,f"found {nullValues} improper nullValues")    
        return rating
        
if __name__ == '__main__':
    PageFixerManager.runCmdLine([NullValueFixer])