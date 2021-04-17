'''
Created on 2021-04-13

@author: wf
'''
import unittest
from openresearch.event import Event,EventSeries
from collections import Counter
from tests.corpus import Corpus

class TestIssue168(unittest.TestCase):
    '''
    add Rating Callback option #168
    '''


    def setUp(self):
        self.debug=True
        pass


    def tearDown(self):
        pass


    def testEventCorpus(self):
        '''
        test the event corpus
        '''
        eventCorpus=Corpus.getEventCorpus(debug=self.debug)
        listOfEvents=eventCorpus.eventList.getList()
        withSeries=0
        for event in listOfEvents:
            self.assertTrue(hasattr(event, 'lastEditor'))
            if hasattr(event,'inEventSeries'): withSeries+=1
        if self.debug:
            print(f"inEventseries: {withSeries}")
        self.assertTrue(withSeries>4500)
            
    
    def checkRatedLod(self,lod,errors,showPainsAbove=11):
        if len(errors)>0:
            for error in errors:
                print(error)
        self.assertEqual(0,len(errors))
        columns=set()
        counters={}
        for record in lod:
            for column in record.keys():
                if column.endswith("PainRating"):
                    if not column in columns:
                        counters[column]=Counter()
                    columns.add(column)
                    rating=record[column]
                    if self.debug:
                        if isinstance(rating.pain,int):
                            if rating.pain>=showPainsAbove:
                                print (rating)
                        else:
                            print(rating) # what?
                    counters[column][rating.pain]+=1
        if self.debug:
            for i,(column,counter) in enumerate(counters.items()):
                print (f"{i+1}:{column}=")
                print(counter.most_common(50))
        pass

    def testRatingCallback(self):
        '''
        test the rating call back
        '''
        eventCorpus=Corpus.getEventCorpus(debug=self.debug)
        lod,errors=eventCorpus.eventList.getRatedLod(Event.rateMigration)
        self.checkRatedLod(lod, errors)
        lod,errors=eventCorpus.eventSeriesList.getRatedLod(EventSeries.rateMigration)
        self.checkRatedLod(lod, errors)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()