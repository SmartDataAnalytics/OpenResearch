from unittest import TestCase

from ormigrate.fixer import ORFixer
from ormigrate.smw.pagefixer import PageFixer, PageFixerManager


class TestPagefixer(TestCase):
    '''
    tests the pagefixer and PageFixerManager functionalities
    '''

    def setUp(self) -> None:
        self.debug=False


    def testPageFixerSubclasses(self):
        pageFixers=PageFixerManager.getAllFixers()
        self.assertTrue(len(pageFixers) > 7)
        if self.debug:
            for pageFixer in pageFixers:
                print(pageFixer.__name__)
