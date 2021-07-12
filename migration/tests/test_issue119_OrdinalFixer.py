'''
Created on 12.07.2021

@author: wf
'''
import unittest
from ormigrate.issue119_ordinal import OrdinalFixer
from ormigrate.toolbox import HelperFunctions as hf
from openresearch.event import Event
from lodstorage.jsonable import Types
from wikifile.wikiFileManager import WikiFileManager

class TestOrdinalFixer(unittest.TestCase):
    '''
    test the ordinal fixer
    '''


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testOrdinalFixer(self):
        '''
            test for fixing Ordinals not a number
            https://github.com/SmartDataAnalytics/OpenResearch/issues/119
        '''
        wikiFileManager=WikiFileManager('orclone')
        fixer=OrdinalFixer.fromWikiFileManager(wikiFileManager)
        lookup_dict = hf.loadDictionary()
        eventRecords= [{'Ordinal':2},
                       {'Ordinal':None},
                       {'Ordinal':'2nd'},
                       {'Ordinal':'test'}]
        expectedPainRatings=[1, 4, 5, 7]
        expectedOrdinals= [2, None, 2, 'test']
        painRatings = []
        ordinals=[]
        for event in eventRecords:
            painRating = fixer.getRating(event)
            res, err = fixer.fixEventRecord(event,lookup_dict)
            ordinals.append(res['Ordinal'])
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
        self.assertEqual(expectedPainRatings,painRatings)
        self.assertEqual(expectedOrdinals, ordinals)
        types = Types("Event")
        samples = Event.getSampleWikiSon()
        fixed=fixer.convertOrdinaltoCardinalWikiFile('sample', samples[0], lookup_dict)
        fixed_dic=hf.wikiSontoLOD(fixed)
        types.getTypes("events", fixed_dic, 1)
        self.assertTrue(types.typeMap['events']['Ordinal'] == 'int')



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()