'''
Created on 2021-04-16

@author: wf
'''

class Rating(object):
    '''
    I am rating
    '''
    missing='❌'
    invalid='👎'
    ok='👍'

    def __init__(self,pain:int,reason:str,hint:str):
        '''
        Constructor
        '''
        self.pain=pain
        self.reason=reason
        self.hint=hint
        
    def __str__(self):
        return f"{self.pain} - {self.reason}: {self.hint}"
        
        