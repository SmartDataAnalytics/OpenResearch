from os import path
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
        '''tests the Module extraction of all fixers'''
        pageFixers=PageFixerManager.getAllFixers()
        self.assertTrue(len(pageFixers) > 7)
        if self.debug:
            for pageFixer in pageFixers:
                print(pageFixer.__name__)


    def testCmdLineRating(self):
        '''test rating functionality of the cmdLine interface'''
        home = path.expanduser("~")
        PageFixerManager.runCmdLine(argv=["-s", "orclone", "--ccId", "orclone-backup", "--targetWikiTextPath", f"{home}/.or/generated/test", "--fixer", "EventSeriesAcronymFixer", "--stats"])

    def testCmdLineRatingWithMultipleFixers(self):
        '''test rating functionality of the cmdLine interface with multiple fixers'''
        home = path.expanduser("~")
        PageFixerManager.runCmdLine(
            argv=["-s", "orclone", "--ccId", "orclone-backup", "--targetWikiTextPath", f"{home}/.or/generated/test",
                  "--fixer", "EventSeriesAcronymFixer", "WikiCFPIDFixer", "--stats", "--tableFormat", "mediawiki"])

    def testCmdLineListRatings(self):
        '''test rating functionality of the cmdLine interface'''
        home = path.expanduser("~")
        PageFixerManager.runCmdLine(argv=["-s", "orclone", "--ccId", "orclone-backup", "--targetWikiTextPath", f"{home}/.or/generated/test", "--fixer", "EventSeriesAcronymFixer", "--listRatings"])
