'''
Created on 2021-04-02

@author: wf
'''
import re
from ormigrate.rating import Rating
from ormigrate.fixer import PageFixer



class AcceptanceRateFixer(PageFixer):

    '''
    fixer for Acceptance Rate Not calculated
    https://github.com/SmartDataAnalytics/OpenResearch/issues/152
    '''

    def __init__(self, wikiClient,debug=False):
        '''
        Constructor
        '''
        # call super constructor
        super(AcceptanceRateFixer,self).__init__(wikiClient)
        self.debug=debug
        self.nosub=0
        self.noacc=0
        self.painrating= None


    def checkfromEvent(self,eventRecord):
        submittedPapers = None
        acceptedPapers = None
        if 'submittedPapers' in eventRecord: submittedPapers = eventRecord['submittedPapers']
        if 'acceptedPapers' in eventRecord: acceptedPapers = eventRecord['acceptedPapers']
        if submittedPapers is None and acceptedPapers is not None:
            self.nosub+=1
        elif submittedPapers is None and acceptedPapers is not None:
            self.noacc+=1


    def check(self,page,event):
        '''
        check the given page and event for missing 'Submitted papers' and 'Accepted Papers' field
        '''
        if len(re.findall(r'\|.*submitted papers.*=.*\n',event.lower())) == 0 and  len(re.findall(r'\|.*accepted papers.*=.*\n',event.lower())) != 0:
            self.nosub+=1
            if self.debug: print(self.generateLink(page))
        elif len(re.findall(r'\|.*submitted papers.*=.*\n',event.lower())) != 0 and  len(re.findall(r'\|.*accepted papers.*=.*\n',event.lower())) == 0:
            if self.debug: print(self.generateLink( page))
            self.noacc+=1

    def result(self):
        text="submitted papers missing for %d: accepted papers missing for: %d" % (self.nosub, self.noacc)
        return text

    @classmethod
    def getRating(self,eventRecord):
        painrating=None
        submittedPapers = None
        acceptedPapers = None
        if 'submittedPapers' in eventRecord: submittedPapers = eventRecord['submittedPapers']
        if 'acceptedPapers' in eventRecord: acceptedPapers = eventRecord['acceptedPapers']
        if submittedPapers is not None and acceptedPapers is not None:
            painrating=Rating(1,Rating.ok,f'Both fields Submitted papers and Accepted Papers are available')
        elif submittedPapers is  None and acceptedPapers is  None:
            painrating=Rating(3,Rating.missing,f'Both fields Submitted papers and Accepted Papers are not available')
        elif submittedPapers is not None and acceptedPapers is None:
            painrating=Rating(5,Rating.missing,f'Submitted papers exists but Accepted Papers is not available')
        elif submittedPapers is None and acceptedPapers is not None:
            painrating=Rating(7,Rating.missing,f'Accepted Papers exists but Submitted papers is not available')
        return painrating

        
if __name__ == "__main__":
    fixer=AcceptanceRateFixer()
    fixer.debug=True
    # fixer.checkAllFiles(fixer.check)
    # print (fixer.result())


