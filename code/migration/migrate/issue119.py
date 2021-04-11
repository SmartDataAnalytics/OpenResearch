'''
Created on 2021-04-07

@author: mk
'''

import re
from migrate.fixer import PageFixer
from migrate.Dictionary import Dictionary
from migrate.toolbox import HelperFunctions

class OrdinalFixer(PageFixer):
    '''
       fixer for Ordinal not being an integer
       https://github.com/SmartDataAnalytics/OpenResearch/issues/119
       '''

    def __init__(self, wikiId="or", baseUrl="https://www.openresearch.org/wiki/", debug=False,restoreOut=False):
        '''
        Constructor
        '''
        # call super constructor
        super(OrdinalFixer, self).__init__(wikiId, baseUrl)
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


if __name__ == "__main__":
    fixer = OrdinalFixer()
    fixer.debug = True
    fixer.fixAllFiles(fixer.convert_ordinal_to_cardinal, "Ordinal", HelperFunctions.loadDictionary())
