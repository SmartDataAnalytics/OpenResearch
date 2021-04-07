'''
Created on 2021-04-02

@author: wf
'''
import re
from migrate.fixer import PageFixer
#from dateutil import parser


class DateFixer(PageFixer):
    '''
    fixer for Acceptance Rate Not calculated
    https://github.com/SmartDataAnalytics/OpenResearch/issues/152
    '''

    def __init__(self, wikiId="ormk", baseUrl="https://www.openresearch.org/wiki/", debug=False,restoreOut=False):
        '''
        Constructor
        '''
        # call super constructor
        super(DateFixer, self).__init__(wikiId, baseUrl)
        self.debug = debug
        self.restoreOut = restoreOut
        

    def getFixedDate(self, page, event):
        '''
        fix the date of the given page and event and mark unfixable pages
        Returns:
            Fixed text of the page.
        '''
        dates = re.findall('.*\|.*date.*=.*\n', event)
        if len(dates) != 0:
            for element in dates:
                name,value=self.getNameValue(element)
                try:
                    fixed = parser.parse(dcheck[-1].strip()).date().strftime("%Y/%m/%d")
                    event= event.replace(element.strip(),dcheck[0].lstrip()+'='+fixed)
                except:
                    prop_div = element.strip().split('=')
                    if len(prop_div[1]) > 0 and '?' not in prop_div[0]:
                        if self.debug: print(self.generateLink(page))
        return event

    def fixFiles(self, filePath, new_file_content):
        if self.restoreOut:
            with open(filePath, mode='w') as fileWrite:
                fileWrite.write(new_file_content)
                print(filePath)
        else:
            with open(filePath, mode='w') as fileWrite:
                fileWrite.write(new_file_content)

    def checkAllFiles(self):
        '''
            check all events
        '''
        for page, event in self.getAllPageTitles4Topic("Event"):
            self.getFixedDate(page, event)

    def fixAllFiles(self,Dictionary):
        for page,event in self.getAllPageTitles4Topic("Event"):
            fixed_page=self.getFixedDate(event,Dictionary)
            self.fixFiles(page,fixed_page)



if __name__ == "__main__":
    fixer = DateFixer()
    fixer.debug = True
    fixer.checkAllFiles()
