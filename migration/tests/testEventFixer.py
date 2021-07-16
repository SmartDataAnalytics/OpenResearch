import unittest
from ormigrate.toolbox import HelperFunctions as hf


class TestEventFixer(unittest.TestCase):
    '''
    test Event fixer
    '''

    def setUp(self) -> None:
        self.debug = False

    def testGetTotalPainRating(self):
        '''
        get the total pain rating for all available fixers
        '''
        pageFixerNames= ['date']
        cache= not hf.inPublicCI()
        eventFixer= EventFixer('orclone')
        eventList = eventFixer.getEventsForPainRating(3,fixerNames=pageFixerNames,cache=cache)
        self.assertGreater(len(eventList.getList()),600)
        if self.debug:print(len(eventList.getList()))