'''
Created on 2021-04-06

@author: wf
'''
from datetime import datetime
from conferencecorpus.corpus.event import EventEntity

from openresearch.openresearch import OpenResearch

 
class OREventSeriesList(EventEntityList):
    '''
    i represent a list of EventSeries
    '''
    propertyLookupList=[
            { 'prop':'EventSeries acronym', 'name': 'acronym',      'templateParam': 'Acronym'},
            { 'prop':'DblpSeries',          'name': 'dblpSeries',   'templateParam': 'DblpSeries'},
            { 'prop':'Homepage',            'name': 'homepage',     'templateParam': 'Homepage'},
            { 'prop':'Logo',                'name': 'logo',         'templateParam': 'Logo'},
            { 'prop':'Title',               'name': 'title',        'templateParam': 'Title'},
            # TODO enable and handle
            #{ 'prop':'Field',      'name': 'subject'},
            { 'prop':'Wikidataid',          'name': 'wikidataId',   'templateParam': 'WikiDataId'},
            { 'prop':'WikiCfpSeries',       'name': 'wikiCfpSeries','templateParam': 'WikiCfpSeries'},
            { 'prop':'Period',              'name': 'period',       'templateParam': 'Period'},
            { 'prop':'Unit',                'name': 'unit',         'templateParam': 'Unit'},
            { 'prop':'Has CORE Rank',       'name': 'core2018Rank', 'templateParam': 'has CORE2018 Rank'}
            # TODO add more fields according to
            # https://confident.dbis.rwth-aachen.de/or/index.php?title=Template:Event_series&action=edit
    ]
    
    def __init__(self):
        '''
        construct me
        '''
        self.eventSeries=[]
        super(OREventSeriesList, self).__init__("eventSeries",EventSeries)
        
class OREventSeries(EventEntity):
    '''
    an event Series
    '''
    # TODO - this is the legacy templateName - make sure after / during migration
    # this is handled properly
    templateName="Event series"
    
    def __init__(self):
        '''
        Constructor
        '''
        
    @classmethod
    def getSamples(self):
        '''
        Returns a sample LOD of an event Series
        '''
        samplesLOD= [{
            'pageTitle': 'AAAI',
            'acronym' : 'AAAI',
            'title' : 'Conference on Artificial Intelligence',
            'subject' : 'Artificial Intelligence',
            'homepage' : 'www.aaai.org/Conferences/AAAI/aaai.php',
            'wikidataId' : 'Q56682083',
            'dblpSeries' : 'aaai',
            'period': 1,
            'unit': 'year'
        },
        {
            "acronym": "3DUI",
            "creationDate": datetime.fromisoformat("2020-03-17T22:54:10"),
            "dblpSeries": "3dui",
            "lastEditor": "Wolfgang Fahl",
            "modificationDate": datetime.fromisoformat("2021-02-13T06:56:46"),
            "pageTitle": "3DUI",
            "title": "IEEE Symposium on 3D User Interfaces",
            "period": "year",
            "unit": 1,
            "wikidataId": "Q105456162"
        },]
        return samplesLOD

    @classmethod
    def getSampleWikiTextList(cls, mode='legacy'):
        '''
        Returns a sample of Event Series in wikison format
        Args:
            mode(str): Default legacy, used to provide the mode dependant on updates and changes to structure of Event series
        '''
        if mode == 'legacy':
            samplesWikiSon = ["""{{Event series
|Acronym=AAAI
|Title=Conference on Artificial Intelligence
|Logo=Aaai-logo.jpg
|has CORE2017 Rank=A*
|Field=Artificial intelligence
|Period=1
|Unit=year
|Homepage=www.aaai.org/Conferences/AAAI/aaai.php
|WikiDataId=Q56682083
|has CORE2018 Rank=A*
|has Bibliography=dblp.uni-trier.de/db/conf/aaai/
|has CORE2014 Rank=A*
|DblpSeries=aaai
}}"""]
        else:
            samplesWikiSon = "..."

        return samplesWikiSon

class EventList(OREntityList):
    propertyLookupList=[
            { 'prop':'Acronym',             'name': 'acronym',         'templateParam': "Acronym"},
            { 'prop':'End date',            'name': 'endDate',         'templateParam': "End date"},
            { 'prop':'Event in series',     'name': 'inEventSeries',   'templateParam': "Series"},
            { 'prop':'Event presence',      'name': 'presence',        'templateParam': "presence"},
            { 'prop':'Event type',          'name': 'eventType',       'templateParam': "Type"},
            { 'prop':'Has_location_country','name': 'country',         'templateParam': "Country"},
            { 'prop':'Has_location_state',  'name': 'region',          'templateParam': "State"},
            { 'prop':'Has_location_city',   'name': 'city',            'templateParam': "City"},
            { 'prop':'Has year',            'name': 'year',            'templateParam': "Year"},   
            { 'prop':'Homepage',            'name': 'homepage',        'templateParam': "Homepage"},
            { 'prop':'Ordinal',             'name': 'ordinal',         'templateParam': "Ordinal"},
            { 'prop':'Start date',          'name': 'startDate',       'templateParam': "Start date"},
            { 'prop':'Title',               'name': 'title',           'templateParam': "Title"},
            { 'prop':'Accepted papers',     'name': 'acceptedPapers',  'templateParam': "Accepted papers"},
            { 'prop':'Submitted papers',    'name': 'submittedPapers', 'templateParam': "Submitted papers"}
    ]               

    '''
    i represent a list of Events
    '''
    def __init__(self):
        self.events=[]
        super(EventList, self).__init__("events",Event)


class Event(OREntity):
    '''
    I represent an Event
    
    see https://rq.bitplan.com/index.php/Event
    '''
    templateName="Event"
    
    def __init__(self):
        '''
        Constructor
        '''
        
    @classmethod
    def getSamples(cls):
        samplesLOD=[{
            "pageTitle": "ICSME 2020",
            "acronym":"ICSME 2020",
            "ordinal": 36,
            "eventType": "Conference",
            "subject": "Software engineering",
            "startDate":  datetime.fromisoformat("2020-09-27"),
            "endDate":  datetime.fromisoformat("2020-09-27")
        },
        {
            "pageTitle": "WebSci 2019",
            "acronym": "WebSci 2019",
            "ordinal": 10,
            "homepage": "http://websci19.webscience.org/",
            "title": "10th ACM Conference on Web Science",
            "eventType": "Conference",
            "startDate": datetime.fromisoformat("2019-06-30"),
            "endDate": datetime.fromisoformat("2019-07-03"),
            "inEventSeries": "WebSci",
            "country": "USA",
            "region": "US-MA",
            "city": "Boston",
            "acceptedPapers": 41,
            "submittedPapers": 120
        },
        {
            "acronym": "5GU 2017",
            "city": "Melbourne",
            "country": "Australia",
            "endDate": datetime.fromisoformat("2017-06-09T00:00:00"),
            "eventType": "Conference",
            "homepage": "http://5guconference.org/2017/show/cf-papers",
            "inEventSeries": "5GU",
            "ordinal": 2,
            "startDate": datetime.fromisoformat("2017-06-08T00:00:00"),
            "title": "2nd EAI International Conference on 5G for Ubiquitous Connectivity",
            # technical attributes - SMW specific
            "pageTitle": "5GU 2017",
            "lastEditor": "Wolfgang Fahl",
            "creationDate": datetime.fromisoformat("2016-09-25T07:36:02"),
            "modificationDate": datetime.fromisoformat("2020-11-05T12:33:23"),
        },
        {
            'acronym': "IDC 2009",
            'title': "The 8th International Conference on Interaction Design and Children",
            'pageTitle': 'IDC 2009',
            'ordinal': 8
        }

        ]
        return samplesLOD
    
    @classmethod
    def getSampleWikiTextList(cls,mode='legacy'):
        if mode=='legacy':
            samplesWikiSon=["""{{Event
|Acronym=ICSME 2020
|Title=36th IEEE International Conference on Software Maintenance and Evolution
|Ordinal=36
|Series=ICSME
|Type=Conference
|Field=Software engineering
|Start date=2020/09/27
|End date=2020/10/03
|Homepage=https://icsme2020.github.io/
|City=Adelaide
|presence=online
|Country=Australia
|Abstract deadline=2020/05/22
|Paper deadline=2020/05/28
|Notification=2020/08/04
|Camera ready=2020/08/25
|Has host organization=Institute of Electrical and Electronics Engineers
|Has coordinator=Sebastian Baltes
|has general chair=Christoph Treude, Hongyu Zhang
|has program chair=Kelly Blincoe, Zhenchang Xing
|has demo chair=Mario Linares Vasquez, Hailong Sun
}}''',
'''36th IEEE International Conference on Software Maintenance and Evolution (ICSME)'''""","""{{Event
|Acronym=AISB 2009
|Ordinal=36
|Title=AISB Symposium: New Frontiers in Human-Robot Interaction
|Type=Conference
|Field=Uncategorized
|Start date=2009/04/08
|End date=2009/04/09
|Submission deadline=2009/01/05
|Homepage=homepages.feis.herts.ac.uk/~comqkd/HRI-AISB2009-Symposium.html
|City=Edinburgh
|Country=United Kingdom
|Notification=2009/02/02
|Camera ready=2009/02/23
}}	
This CfP was obtained from [http://www.wikicfp.com/cfp/servlet/event.showcfp?eventid=3845&amp;copyownerid=2048 WikiCFP]
"""]
        else:
            samplesWikiSon="..."
        
        return samplesWikiSon
    