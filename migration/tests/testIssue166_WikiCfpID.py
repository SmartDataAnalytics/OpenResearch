'''
Created on 2021-07-16

@author: wf
'''
import unittest
from ormigrate.issue166_cfp import WikiCFPIDFixer
from corpus.datasources.openresearch import OREvent
from tests.pagefixtoolbox import PageFixerTest
from wikifile.wikiFile import WikiFile
from ormigrate.smw.rating import EntityRating

class TestWikiCFPId(PageFixerTest):
    '''
    test wiki CFP Id fixing
    '''
    
    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=WikiCFPIDFixer
        #self.testAll=False


    def testIssue166Examples(self):
        """
        Tests the issue 166 for addition of WikiCFP-ID to applicable pages.
        Testing the fix function

        """
        fixer=self.getPageFixer()
        samplesWikiText = OREvent.getSampleWikiTextList()
        wikicfpid= fixer.getWikiCFPIdFromPage(samplesWikiText[1])
        self.assertIsNotNone(wikicfpid)
        self.assertEqual(wikicfpid, 3845)

        wikiFile = WikiFile(name='sampleFile', wikiFileManager=None, wikiText=samplesWikiText)
        event = OREvent()
        entityRating = EntityRating(event, pageTitle='Test')
        entityRating.templateName = 'Event'
        entityRating.wikiFile = wikiFile

        # Get Fixer
        fixer = self.getPageFixer()

        # Rate With Fixer
        fixer.rate(entityRating)
        if self.debug:
            print(entityRating)
        self.assertEqual(entityRating.pain, 5)

        # Fix With Fixer
        fixer.fix(entityRating)
        self.assertEqual(entityRating.entity.wikicfpId, 3845)

    def testGetWikiCFPIdFromPage(self):
        """
        tests extracting the wikiCfpId from a given wikiText string.
        """
        fixer = self.getPageFixer()
        entity = self.getTestEntity()
        wikiCfpId = fixer.getWikiCFPIdFromPage(entity.wikiFile.wikiText)
        self.assertEqual(1773, wikiCfpId)

    def testIssue166Rating(self):
        """
        test the Rating function of the fixer
        """
        fixer = self.getPageFixer()
        # test wikicfpId not set but present
        rating = self.getTestEntity()
        fixer.rate(rating)
        self.assertEqual(5, rating.pain)
        # test wikicfpId set
        setattr(rating.entity, "wikicfpId", 1773)
        fixer.rate(rating)
        self.assertEqual(1, rating.pain)

    def testIssue166(self):
        '''
        test the wikicfpID handling
        '''
        pageTitleLists = self.getPageTitleLists("WebDB 2008", "WebS 2008", "WiCOM 2008", "WiCOM 2009", "WiCOM 2010",
                                                "WiMob 2008", "WiNC 2009", "WiOpt 2008")
        for pageTitleList in pageTitleLists:
            counters = self.getRatingCounters(pageTitleList)
            painCounter = counters["pain"]
            if pageTitleList is not None:
                self.assertEqual(8, painCounter[self.pageFixerClass.__name__][1])
            else:
                self.assertGreaterEqual(painCounter[self.pageFixerClass.__name__][1], 2400)
                self.assertGreaterEqual(painCounter[self.pageFixerClass.__name__][5], 3)

    def getTestEntity(self) -> EntityRating:
        """
        Returns a test Entity
        """
        page = """{{Event
         | Acronym = WiMob 2008
         | Title = IEEE International Conference on Wireless and Mobile Computing, Networking and Communications
         | Type = Conference
         | Series = 
         | Field = Computer networking
         | Homepage = www.lia.univ-avignon.fr/wimob2008
         | Start date = Oct 12, 2008 
         | End date =  Oct 15, 2008
         | City= Avignon
         | State = 
         | Country =  France
         | Abstract deadline = Aug 1, 2008
         | Submission deadline = May 16, 2008
         | Notification = 
         | Camera ready = 
        }}

        <pre>
            The research area of mobile computing has become more important following the recent widespread drive towards mobile ad hoc networks, wireless sensor networks and vehicular ad hoc networks tracking technologies and their applications. The availability of the high bandwidth 3G infrastructures, and the pervasive deployment of low cost WiFi infrastructure and WiMAX to create hotspots around the world serve to accelerate the development of
            mobile computing towards ubiquitous computing.

            WiMob'08 addresses three main areas: Wireless Communications, Mobile Networking, Ubiquitous Computing and Applications. This conference aims to stimulate interactions among participants and enable them to exchange new ideas and practical experience in these areas.
        	</pre>This CfP was obtained from [http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid=1773&amp;copyownerid=2 WikiCFP][[Category:Computer networking]]
        [[Category:Mobile computing]]"""
        rating = self.getEntityRatingFromDict({"pageTitle": "WiMob 2008"}, wikiText=page)
        return rating


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()