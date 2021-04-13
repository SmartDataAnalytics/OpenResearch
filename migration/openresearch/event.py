'''
Created on 2021-04-06

@author: wf
'''
from lodstorage.jsonable import JSONAble,JSONAbleList
from datetime import datetime
from wikibot.wikiuser import WikiUser
from wikibot.wikiclient import WikiClient
from wikibot.wikipush import WikiPush
from pathlib import Path
import os
import time


class OREntityList(JSONAbleList):
    '''
    wrapper for JSONAble
    '''
    def __init__(self,listName:str=None,clazz=None,tableName:str=None):
        super(OREntityList, self).__init__(listName,clazz,tableName)
        self.profile=False
        self.debug=False
        self.wikiClient=None
        self.wikiPush=None
        self.askExtra=""
        
    def getList(self):
        return self.__dict__[self.listName]
    
    def getEntityName(self):
        '''
        get my entity name
        '''
        return self.clazz.__name__
    
    def getAskQuery(self,propertyLookupList,askExtra=""):
        '''
        get the query that will ask for all my events
        
        Args:
            propertyLookupList:  a list of dicts for propertyLookup
           askExtra(str): any additional constraints
        '''
        entityName=self.getEntityName()
        isASelector="IsA::%s" % entityName
        selector="Category:Event series" if entityName=="EventSeries" else isASelector
        ask="""{{#ask:[[%s]]%s
|mainlabel=pageTitle""" % (selector,askExtra)
        for propertyLookup in propertyLookupList:
            propName=propertyLookup['prop']
            name=propertyLookup['name']
            ask+="|?%s=%s\n" % (propName,name)
        ask+="}}"
        return ask
    
    @staticmethod        
    def getCachePath():
        home = str(Path.home())
        cachedir="%s/.or/" %home
        return cachedir
    
    def getJsonFile(self):
        '''
        get the json File for me
        '''
        cachePath=OREntityList.getCachePath()
        os.makedirs(cachePath,exist_ok=True)
        jsonPrefix="%s/%s" % (cachePath,self.getEntityName())
        jsonFilePath="%s.json" % jsonPrefix
        return jsonFilePath
    
    def fromCache(self,wikiuser:WikiUser):
        '''
        Args:
            wikiuser: the wikiuser to use 
        '''
        jsonFilePath=self.getJsonFile()
        # TODO: fix upstream pyLodStorage
        jsonPrefix=jsonFilePath.replace(".json","")
        if os.path.isfile(jsonFilePath):
            self.restoreFromJsonFile(jsonPrefix)
        else:
            self.fromWiki(wikiuser,askExtra=self.askExtra,profile=self.profile)
            self.storeToJsonFile(jsonPrefix)
            
    def fromWiki(self,wikiuser:WikiUser,askExtra="",profile=False):
        '''
        read me from a wiki using the givne WikiUser configuration
        '''
        if self.wikiClient is None:
            self.wikiclient=WikiClient.ofWikiUser(wikiuser)
            self.wikiPush = WikiPush(fromWikiId=wikiuser.wikiId)
        askQuery=self.getAskQuery(askExtra)
        if self.debug:
            print(askQuery)
        startTime=time.time()
        entityName=self.getEntityName()
        records = self.wikiPush.formatQueryResult(askQuery, self.wikiClient, entityName=entityName)
        elapsed=time.time()-startTime
        if profile:
            print("query of %d %s records took %5.1f s" % (len(records),entityName,elapsed))
        self.fromLoD(records)
        return records
    
    def fromSQLTable(self,sqlDB,entityInfo):
        lod=sqlDB.queryAll(entityInfo)
        self.fromLoD(lod)
        
    def fromLoD(self,lod): 
        '''
        create me from the given list of dicts
        '''
        errors=[] 
        entityList=self.getList()  
        for record in lod:
            # call the constructor to get a new instance
            try:
                entity=self.clazz()
                if hasattr(entity,"fixRecord"):
                    fixRecord=getattr(entity,'fixRecord');
                    if callable(fixRecord):
                        fixRecord(record)
                entity.fromDict(record)
                entityList.append(entity)
            except Exception as ex:
                error={
                    self.getEntityName():record,
                    "error": ex
                }
                errors.append(error)
                if self.debug:
                    print(error)
        return errors
        
class EventSeriesList(OREntityList):
    '''
    i represent a list of EventSeries
    '''
    def __init__(self):
        self.eventSeries=[]
        super(EventSeriesList, self).__init__("eventSeries",EventSeries)
    
    def getAskQuery(self,askExtra=""):
        '''
        get the query that will ask for all my events
        
        Args:
           askExtra(str): any additional constraints
        '''
        propertyLookupList=[
            { 'prop':'Acronym',    'name': 'acronym'},
            { 'prop':'Homepage',   'name': 'homepage'},
            { 'prop':'Title',      'name': 'title'},
            #{ 'prop':'Field',      'name': 'subject'},
            { 'prop':'WikiDataId',  'name': 'wikiDataId'},
            { 'prop':'DblpSeries',  'name': 'dblpSeries' }
        ]               
        ask=super().getAskQuery(propertyLookupList,askExtra)
        return ask
        
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
    
    def __str__(self):
        text=self.pageTitle
        if hasattr(self, "acronym"):
            text+="(%s)" %self.acronym
        return text

class EventList(OREntityList):
    '''
    i represent a list of Events
    '''
    def __init__(self):
        self.events=[]
        super(EventList, self).__init__("events",Event)
    
    def getAskQuery(self,askExtra=""):
        '''
        get the query that will ask for all my events
        
        Args:
           askExtra(str): any additional constraints
        '''
        propertyLookupList=[
            { 'prop':'Acronym',             'name': 'acronym'},
            { 'prop':'Ordinal',             'name': 'ordinal'},
            { 'prop':'Homepage',            'name': 'homepage'},
            { 'prop':'Title',               'name': 'title'},
            { 'prop':'Event type',          'name': 'eventType'},
            { 'prop':'Start date',          'name': 'startDate'},
            { 'prop':'End date',            'name': 'endDate'},
            { 'prop':'Event in series',     'name': 'inEventSeries'},
            { 'prop':'Has_location_country','name': 'country'},
            { 'prop':'Has_location_state',  'name': 'region'},
            { 'prop':'Has_location_city',   'name': 'city'},
            { 'prop':'Accepted_papers',     'name': 'acceptedPapers'},
            { 'prop':'Submitted_papers',    'name': 'submittedPapers'}
        ]               
        ask=super().getAskQuery(propertyLookupList,askExtra)
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
            "evenType": "Conference",
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
        }
        ]
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
    
    def fixRecord(self,record):
        '''
        fix my dict representation
        '''
        invalidKeys=[]
        for key in record.keys():
            value=record[key]
            if type(value)==list:
                # TODO: handle properly e.g. by marking and converting list to 
                # comma separated list
                invalidKeys.append(key)
                print ("%s=%s in %s"  % (key,record[key],record ))
            if value is None:
                invalidKeys.append(key)
                
        for key in invalidKeys:
            record.pop(key)
            
    
    def __str__(self):
        text=self.pageTitle
        if hasattr(self, "acronym"):
            text+="(%s)" %self.acronym
        return text
    
class CountryList(JSONAbleList):
    '''
    a list of countries
    '''
    def __init__(self):
        self.countries=[]
        super(CountryList, self).__init__("countries",Country)

class Country(JSONAble):
    '''
    distinct region in geography; a broad term that can include political divisions or 
    regions associated with distinct political characteristics 
    '''
    
    @classmethod
    def getSamples(cls):
        '''
        get my samples
        TODO:
           remove countryPrefix and change country attribute to "name"
        '''
        samplesLOD=[
    {
      "name" : "USA",
      "wikidataName" : "United States of America",
      "wikidataId" : "Q30"
    },
    {
      "name" : "China",
      "wikidataName" : "People's Republic of China",
      "wikidataId" : "Q148"
    },
    {
      "name" : "Germany",
      "wikidataName" : "Germany",
      "wikidataId" : "Q183"
    },
    {
      "name" : "Italy",
      "wikidataName" : "Italy",
      "wikidataId" : "Q38"
    },
    {
      "name" : "France",
      "wikidataName" : "France",
      "wikidataId" : "Q142"
    }
    ]
        return samplesLOD
    
    def __str__(self):
        text=self.name
        return text
    