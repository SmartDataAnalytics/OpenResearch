import os
import tempfile
from os import path
from ormigrate.smw.pagefixer import PageFixerManager
from tests.basetest import BaseTest
from tests.corpusfortesting import CorpusForTesting


class TestPagefixer(BaseTest):
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

    def testGenerateTechnicalEntityPages(self):
        '''tests the generation of the entity pages'''
        with tempfile.TemporaryDirectory() as tmpdirname:
            wikiFileManager=CorpusForTesting.getWikiFileManager(targetDir=tmpdirname)
            manager=PageFixerManager([],wikiFileManager)
            manager.generateTechnicalEntityPages(wikiFileManager,True)
            #check if template pages are generated
            for entity in ["Event","Event series","Rating","Fixer"]:
                self.assertTrue(os.path.isfile(f"{wikiFileManager.targetPath}/Template:{entity}.wiki"))

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

    def testCmdLineAddRatingPages(self):
        '''test rating functionality of the cmdLine interface'''
        home = path.expanduser("~")
        PageFixerManager.runCmdLine(argv=["-s", "orclone", "--ccId", "orclone-backup", "--targetWikiTextPath", f"{home}/.or/generated/rating","--fixer", "EventSeriesAcronymFixer", "SeriesFixer", "--addRatingPage"])

    def testCmdLineFix(self):
        '''test rating functionality of the cmdLine interface'''
        home = path.expanduser("~")
        PageFixerManager.runCmdLine(argv=["-s", "orclone", "--ccId", "orclone-backup", "--targetWikiTextPath", f"{home}/.or/generated/test", "--fixer", "EventSeriesAcronymFixer", "--fix", "--force"])

    def testGenerateFixerPages(self):
        home = path.expanduser("~")
        fixer=[fixer.__name__ for fixer in PageFixerManager.getAllFixers()]
        manager=PageFixerManager.runCmdLine( argv=["-s", "orclone", "--ccId", "orclone-backup", "--targetWikiTextPath", f"{home}/.or/generated/fixer","--fixer",*fixer])
        manager.generateFixerPages(overwrite=True)