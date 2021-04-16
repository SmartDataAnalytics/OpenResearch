'''
Created on 2021-04-06

@author: wf
'''
import re
from ormigrate.fixer import PageFixer
from ormigrate.toolbox import HelperFunctions as hf


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
        change=False
        dates = re.findall('|.*'+datetype+'.*=.*\n', event)
        if len(dates) != 0:
            for element in dates:
                name,value=self.getNameValue(element)
                if name is not None and value is not None:
                    fixedDate = hf.parseDate(value)
                    if fixedDate is not None:
                        if fixedDate != value:
                            change = True
                        event = event.replace(element,'|'+name+'='+fixedDate)
                    else:
                        generateLink=True
        if self.debug and generateLink: print(self.generateLink(page))
        if change:
            return event
        else:
            return None

    def getRating(self,eventRecord):
        painrating= None
        if eventRecord['startDate'] is not None and eventRecord['endDate'] is not None:
            fixedStartDate = hf.parseDate(eventRecord['startDate'])
            fixedEndDate= hf.parseDate(eventRecord['endDate'])
            if fixedStartDate is None and fixedEndDate is None:
                painrating = 7
            elif fixedStartDate is None:
                painrating = 6
            elif fixedEndDate is None:
                painrating= 5
            else:
                painrating=1
        elif eventRecord['startDate'] is None and eventRecord['endDate'] is None:
            painrating=2
        elif eventRecord['startDate'] is None and eventRecord['endDate'] is not None:
            painrating=4
            fixedDate=hf.parseDate(eventRecord['endDate'])
            if fixedDate is None:
                painrating= 6
        elif eventRecord['startDate'] is not None and eventRecord['endDate'] is None:
            painrating=3
            fixedDate = hf.parseDate(eventRecord['startDate'])
            if fixedDate is None:
                painrating = 6
        return painrating





if __name__ == "__main__":
    fixer = DateFixer()
    fixer.debug = True
    # fixer.checkAllFiles(fixer.getFixedDate, 'deadline')
    fixer.fixAllFiles(fixer.getFixedDate, "Date", 'date')
    fixer.fixAllFiles(fixer.getFixedDate, "Deadline", 'deadline')
