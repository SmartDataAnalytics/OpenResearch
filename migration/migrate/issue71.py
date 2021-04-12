'''
Created on 2021-04-06

@author: wf
'''
import re
from migrate.fixer import PageFixer
from dateutil import parser
from migrate.toolbox import HelperFunctions


class DateFixer(PageFixer):
    '''
    fixer for Acceptance Rate Not calculated
    https://github.com/SmartDataAnalytics/OpenResearch/issues/152
    '''

    def __init__(self, wikiId="or", baseUrl="https://www.openresearch.org/wiki/", debug=False,restoreOut=False):
        '''
        Constructor
        '''
        # call super constructor
        super(DateFixer, self).__init__(wikiId, baseUrl)
        self.debug = debug
        self.restoreOut = restoreOut


    def getFixedDate(self, page, event, datetype='date'):
        '''
        fix the date of the given page and event and mark unfixable pages
        Returns:
            Fixed text of the page.
        '''
        generateLink=False
        dates = re.findall('|.*'+datetype+'.*=.*\n', event)
        if len(dates) != 0:
            for element in dates:
                name,value=self.getNameValue(element)
                if name is not None and value is not None:
                    fixedDate = HelperFunctions.parseDate(value)
                    if fixedDate is not None:
                        event = event.replace(element,'|'+name+'='+fixedDate)
                    else:
                        generateLink=True
        if self.debug and generateLink: print(self.generateLink(page))
        return event





if __name__ == "__main__":
    fixer = DateFixer()
    fixer.debug = True
    # fixer.checkAllFiles(fixer.getFixedDate, 'deadline')
    fixer.fixAllFiles(fixer.getFixedDate, "Date", 'date')
    fixer.fixAllFiles(fixer.getFixedDate, "Deadline", 'deadline')
