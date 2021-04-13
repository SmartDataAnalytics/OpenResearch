'''
Created on 2021-04-02

@author: wf
'''
import re
from ormigrate.fixer import PageFixer

class AcceptanceRateFixer(PageFixer):

    '''
    fixer for Acceptance Rate Not calculated
    https://github.com/SmartDataAnalytics/OpenResearch/issues/152
    '''

    def __init__(self, wikiId="or",baseUrl="https://www.openresearch.org/wiki/",debug=False):
        '''
        Constructor
        '''
        # call super constructor
        super(AcceptanceRateFixer,self).__init__(wikiId,baseUrl)
        self.debug=debug
        self.nosub=0
        self.noacc=0

    

    def check(self,page,event):
        '''
        check the given page and event for missing 'Submitted papers' and 'Accepted Papers' field
        '''
        if len(re.findall('\|.*submitted papers.*=.*\n',event.lower())) == 0 and  len(re.findall('\|.*accepted papers.*=.*\n',event.lower())) != 0:
            self.nosub+=1
            if self.debug: print(self.generateLink(page))
        elif len(re.findall('\|.*submitted papers.*=.*\n',event.lower())) != 0 and  len(re.findall('\|.*accepted papers.*=.*\n',event.lower())) == 0:
            if self.debug: print(self.generateLink( page))
            self.noacc+=1

    def result(self):
        text="submitted papers missing for %d: accepted papers missing for: %d" % (self.nosub, self.noacc)
        return text

        
if __name__ == "__main__":
    fixer=AcceptanceRateFixer()
    fixer.debug=True
    fixer.checkAllFiles(fixer.check)
    print (fixer.result())


