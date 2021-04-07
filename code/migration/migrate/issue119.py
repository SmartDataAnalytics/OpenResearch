import re
from migrate.fixer import PageFixer
from migrate.Dictionary import Dictionary
from os import path

class OrdinalFixer(PageFixer):
    '''
       fixer for Ordinal not being an integer
       https://github.com/SmartDataAnalytics/OpenResearch/issues/119
       '''

    def __init__(self, wikiId="ormk", baseUrl="https://www.openresearch.org/wiki/", debug=False,dry_run=True,restoreOut=False):
        '''
        Constructor
        '''
        # call super constructor
        super(OrdinalFixer, self).__init__(wikiId, baseUrl)
        self.debug = debug
        self.dry_run = dry_run
        self.restoreOut = restoreOut

    def convert_ordinal_to_cardinal(self, file_content: str, lookup_dict: Dictionary):
        pattern = r"{{ *Event(?:.|\r|\n)*\| *Ordinal *= *(?P<ordinal>[^\|\n}]*) *[\n|}}|\|]"
        match = re.search(pattern, file_content)
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
                    new_file_content = file_content[0: start:] + cardinal_value + file_content[stop::]
                    if self.dry_run and self.debug:
                            print(f"{ordinal_val} will changed to {cardinal_value}.")
                    return new_file_content

    def fixFile(self, filePath, new_file_content):
        '''
        separate concerns of fixing/writing and gathering a list of files that haven been fixed
        fix the given file
        
        Args:
            filePath(str): 
        '''
        with open(filePath, mode='w') as fileWrite:
                fileWrite.write(new_file_content)
            
    def fixAllFiles(self,fileList):
        for page,event in self.getAllPageTitles4Topic("Event"):
            self.check(event,Dictionary)
