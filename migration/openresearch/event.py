'''
Created on 2021-04-06

@author: wf
'''
from lodstorage.jsonable import JSONAble,JSONAbleList, Types
from datetime import datetime
class EventSeriesList(JSONAbleList):
    '''
    i represent a list of EventSeries
    '''
    def __init__(self):
        self.eventSeries=[]

    def fromSQLTable(self,sqlDB,entityInfo):
        lod=sqlDB.queryAll(entityInfo)
        for record in lod:
            eventSeries=EventSeries()
            eventSeries.fromDict(record)
            self.eventSeries.append(eventSeries)
        pass
        
class EventSeries(JSONAble):
    '''
    '''
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
            'Title' : 'Conference on Artificial Intelligence',
            'Field' : 'Artificial Intelligence',
            'Homepage' : 'www.aaai.org/Conferences/AAAI/aaai.php',
            'WikiDataId' : 'Q56682083',
            'DblpSeries' : 'aaai'
        }]
        return samplesLOD

    @classmethod
    def getSampleWikiSon(cls, mode='legacy'):
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

class EventList(JSONAbleList):
    '''
    i represent a list of Events
    '''
    def __init__(self):
        self.events=[]
        
    def fromSQLTable(self,sqlDB,entityInfo):
        lod=sqlDB.queryAll(entityInfo)
        for record in lod:
            event=Event()
            event.fromDict(record)
            self.events.append(event)
        pass
    
    
    def getAskQuery(self,askExtra=""):
        '''
        get the query that will ask for all my events
        
        Args:
           askExtra(str): any additional constraints
        '''
        ask="""{{#ask:[[IsA::Event]]%s
|mainlabel=pageTitle""" % askExtra
        propertyLookupList=[
            { 'prop':'Acronym',    'name': 'acronym'},
            { 'prop':'Ordinal',    'name': 'ordinal'},
            { 'prop':'Homepage',   'name': 'homepage'},
            { 'prop':'Title',      'name': 'title'},
            { 'prop':'Type',       'name': 'type'},
            { 'prop':'Start date', 'name': 'startDate'},
            { 'prop':'End date',   'name': 'endDate'}
        ]               
        for propertyLookup in propertyLookupList:
            propName=propertyLookup['prop']
            name=propertyLookup['name']
            ask+="|?%s=%s\n" % (propName,name)
        ask+="}}"
        return ask
    
class Event(JSONAble):
    '''
    I represent an Event
    
    see https://rq.bitplan.com/index.php/Event
    '''
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
            "type": "Conference",
            "subject": "Software engineering",
            "startDate":  datetime.fromisoformat("2020-09-27"),
            "endDate":  datetime.fromisoformat("2020-09-27")
        }]
        return samplesLOD
    
    @classmethod
    def getSampleWikiSon(cls,mode='legacy'):
        if mode=='legacy':
            samplesWikiSon=["""{{Event
|Acronym=ICSME 2020
|Title=36th IEEE International Conference on Software Maintenance and Evolution
|Series=ICSME
|Ordinal=36th
|Type=Conference
|Field=Software engineering
|Start date=27th Sept, 2020
|End date=2020/10/03
|Homepage=https://icsme2020.github.io/
|City=Adelaide
|State=Online
|Country=Australia
|Abstract deadline=2020/05/22
|Paper deadline=28th May, 2020
|Notification=2020/08/04
|Camera ready=2020/08/25
|Has host organization=Institute of Electrical and Electronics Engineers
|Has coordinator=Sebastian Baltes
|has general chair=Christoph Treude, Hongyu Zhang
|has program chair=Kelly Blincoe, Zhenchang Xing
|has demo chair=Mario Linares Vasquez, Hailong Sun
}}"""]
        else:
            samplesWikiSon="..."
        
        return samplesWikiSon

    def __str__(self):
        text=self.pageTitle
        return text
