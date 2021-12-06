'''
Created on 2021-04-07

@author: mk
'''

import re
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer, Entity
from ormigrate.smw.rating import Rating, RatingType, EntityRating
from ormigrate.dictionary import Dictionary
from ormigrate.toolbox import HelperFunctions as hf

class OrdinalFixer(ORFixer):
    '''
    see purpose and issue     
    '''
    purpose="fixer for Ordinal not being an integer"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/119"

    worksOn = [Entity.EVENT]
    
    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(OrdinalFixer, self).__init__(pageFixerManager)
        self.lookup_dict = hf.loadDictionary()

    def fix(self,rating:EntityRating):

        record=rating.getRecord()
        self.fixEventRecord(record, self.lookup_dict)

    def fixEventRecord(self,event:dict,lookup_dict: Dictionary, errors=None):
        if errors is None:
            errors={}
        ordinal_val = str(event.get('ordinal'))
        if not ordinal_val.isnumeric():
            cardinal_dict = lookup_dict.getToken(ordinal_val)
            if cardinal_dict is None:
                errors['lookupnotfound'] = True
                CRED = '\033[91m'
                CEND = '\033[0m'
                if self.debug:
                    print(f"{CRED}:\t Lookup failed! {ordinal_val} is missing in the dictionary. {CEND}")
            else:
                cardinal_value = cardinal_dict['value']
                event['ordinal'] = cardinal_value
                if self.debug:
                    print(f"{ordinal_val} will changed to {cardinal_value}.")
        else:
            # ordinal is string and numeric
            event['ordinal'] = int(ordinal_val)
        return event,errors


    def convertOrdinaltoCardinalWikiFile(self, page, event, lookup_dict: Dictionary):
        '''
        Converts the ordinal value to cardinal value in the given event
        Args:
            event(str): wiki file content in string
            lookup_dict(Dictionary): Dictionary for mapping of ordinals
        Returns:
            new_event(str):Page text with fixed ordinal
        '''
        pattern = r"{{ *Event(?:.|\r|\n)*\| *Ordinal *= *(?P<ordinal>[^\|\n}]*) *[\n|}}|\|]"
        match = re.search(pattern, event)
        if match:
            ordinal_val = match.group('ordinal')
            if not ordinal_val.isnumeric():
                (start, stop) = match.span('ordinal')
                cardinal_dict = lookup_dict.getToken(ordinal_val)
                if cardinal_dict is None:
                    CRED = '\033[91m'
                    CEND = '\033[0m'
                    if self.debug:
                        print(f"{CRED}:\t Lookup failed! {ordinal_val} is missing in the dictionary. {CEND}")
                else:
                    cardinal_value = str(cardinal_dict['value'])
                    new_event = event[0: start:] + cardinal_value + event[stop::]
                    if self.debug:
                            print(f"{ordinal_val} will changed to {cardinal_value}.")
                    return new_event

    def rate(self, rating: EntityRating):
        aRating=self.getRating(rating.getRecord())
        rating.set(pain=aRating.pain, reason=aRating.reason, hint=aRating.hint)
        return rating

    @classmethod
    def getRating(cls,eventRecord):
        '''
        get the pain rating for the given eventRecord
        '''
        painRating = None
        # TODO: this looks modal
        value=None
        if 'Ordinal' in eventRecord: value=eventRecord['Ordinal']
        if 'ordinal' in eventRecord: value=eventRecord['ordinal']
        if value is None:
            painRating = Rating(4,RatingType.missing,'Ordinal is missing')
        else:
            if type(value) == str and value.isnumeric():
                value=int(value)
            if type(value) == int:
                if value<1 or value>100:
                    painRating=Rating(7,RatingType.invalid,f'Ordinal {value} out of range 1-100')
                painRating = Rating(1,RatingType.ok,f'Ordinal {value} valid and in range 1-100')
            elif type(value) == str:
                if any(char.isdigit() for char in value):
                    painRating = Rating(5,RatingType.invalid,f'Ordinal {value} is not a number')
                else:
                    painRating = Rating(7,RatingType.invalid,f'Ordinal {value} is not a number')
        return painRating

if __name__ == '__main__':
    PageFixerManager.runCmdLine([OrdinalFixer])