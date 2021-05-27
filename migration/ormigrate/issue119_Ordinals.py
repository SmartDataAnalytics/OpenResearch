'''
Created on 2021-04-07

@author: mk
'''

import re
from ormigrate.rating import Rating
from ormigrate.fixer import PageFixer
from ormigrate.dictionary import Dictionary
from ormigrate.toolbox import HelperFunctions

class OrdinalFixer(PageFixer):
    '''
       fixer for Ordinal not being an integer
       https://github.com/SmartDataAnalytics/OpenResearch/issues/119
       '''

    def __init__(self, wikiClient, debug=False,restoreOut=False):
        '''
        Constructor
        '''
        # call super constructor
        super(OrdinalFixer, self).__init__(wikiClient)
        self.debug = debug
        self.restoreOut = restoreOut

    def convert_ordinal_to_cardinal(self, page, event, lookup_dict: Dictionary):
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
            painRating = Rating(4,Rating.missing,'Ordinal is missing')
        elif type(value) == int:
            if value<1 or value>100:
                painRating=Rating(7,Rating.invalid,f'Ordinal {value} out of range 1-100')
            painRating = Rating(1,Rating.ok,f'Ordinal {value} valid and in range 1-100')
        elif type(value) == str:
            if any(char.isdigit() for char in value):
                painRating = Rating(5,Rating.invalid,f'Ordinal {value} is not a number')
            else:
                painRating = Rating(7,Rating.invalid,f'Ordinal {value} is not a number')
        return painRating

if __name__ == "__main__":
    fixer = OrdinalFixer()
    fixer.debug = True
    fixer.fixAllFiles(fixer.convert_ordinal_to_cardinal, "Ordinal", HelperFunctions.loadDictionary())
