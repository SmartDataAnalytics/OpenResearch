import unittest
from ormigrate.eventFixer import EventFixer
from ormigrate.issue71_date import DateFixer
from ormigrate.toolbox import HelperFunctions as hf


class TestEventFixer(unittest.TestCase):
    '''
    test Event fixer
    '''

    def setUp(self) -> None:
        self.debug = False

    def testgetPainRating(self):
        pageFixerNames= ['date']
        cache= not hf.inPublicCI()
        eventFixer= EventFixer('orclone')
        eventList = eventFixer.getEventsForPainRating(3,fixerNames=pageFixerNames,cache=cache)
        self.assertGreater(len(eventList.getList()),600)
        if self.debug:print(len(eventList.getList()))