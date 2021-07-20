'''
Created on 2021-04-06

@author: wf
'''
from lodstorage.jsonable import JSONAble,JSONAbleList
from collections import OrderedDict
from datetime import datetime

from lodstorage.lod import LOD
from wikibot.wikiuser import WikiUser
from wikibot.wikiclient import WikiClient
from wikibot.wikipush import WikiPush
from wikifile.wikiFileManager import WikiFileManager
from wikifile.wikiFile import WikiFile

import os
import time
from openresearch.openresearch import OpenResearch

class OREntity(JSONAble):
    '''
    base class for OpenResearch entities
    '''
    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def __str__(self):
        '''
        return my
        '''
        text=self.__class__.__name__
        attrs=["pageTitle","acronym","title"]
        delim=":"
        for attr in attrs:
            if hasattr(self, attr):
                value=getattr(self,attr)
                text+=f"{delim}{value}"
                delim=":" 
        return text
        
    @staticmethod
    def fromWikiSonToLod(record:dict,lookup:dict)->dict:
        '''
        convert the given record from wikiSon to list of dict with the given lookup map
        
        Args:
            record(dict): the original record in WikiSon format
            lookup(dict): the mapping of keys/names for the name/value pairs
        Return:
            dict: a dict which replaces name,value pairs with lookup[name],value pairs
        ''' 
        result=None 
        if record:
            result={}
            for key in lookup:
                if key in record:
                    newKey=lookup[key].get('name')
                    if newKey is not None:
                        result[newKey]=record[key]
                        #del record[key]
        return result

    def fixRecord(self, record):
        '''
        fix my dict representation
        '''
        invalidKeys = []
        for key in record.keys():
            value = record[key]
            if type(value) == list:
                # TODO: handle properly e.g. by marking and converting list to
                # comma separated list

                invalidKeys.append(key)
                print("invalid list %s=%s in %s" % (key, record[key], record))
            if value is None:
                invalidKeys.append(key)

        for key in invalidKeys:
            record.pop(key)

class OREntityList(JSONAbleList):
    '''
    OpenResearch entity list
    '''
    def __init__(self,listName:str=None,clazz=None,tableName:str=None):
        super(OREntityList, self).__init__(listName,clazz,tableName)
        self.profile=False
        self.debug=False
        self.wikiClient=None
        self.wikiPush=None
        self.wikiFileManager=None
        self.askExtra=""

    def getList(self):
        return self.__dict__[self.listName]

    def updateEntity(self,entity,identifier='pageTitle'):
        '''
        Add/Update the given entity in the entityList
        '''
        if hasattr(entity,identifier):
            attributes = [*entity.__dict__]
            for origEntity in self.getList():
                if origEntity.pageTitle == entity.pageTitle:
                    origAttributes = [*origEntity.__dict__]
                    difference = set(attributes) - set(origAttributes)
                    for attr in difference:
                        setattr(origEntity,attr,getattr(entity,attr))
                    return
            self.getList().append(entity)
        else:
            raise Exception('identifier not found in entity given')

    def getEntityName(self):
        '''
        get my entity name
        '''
        return self.clazz.__name__

    def getAskQuery(self,askExtra="",propertyLookupList=None):
        '''
        get the query that will ask for all my events

        Args:
           askExtra(str): any additional SMW ask query constraints
           propertyLookupList:  a list of dicts for propertyLookup

        Return:
            str: the SMW ask query
        '''
        entityName=self.getEntityName()
        selector="IsA::%s" % entityName
        ask="""{{#ask:[[%s]]%s
|mainlabel=pageTitle
|?Creation date=creationDate
|?Modification date=modificationDate
|?Last editor is=lastEditor
""" % (selector,askExtra)
        if propertyLookupList is None:
            propertyLookupList=self.propertyLookupList
        for propertyLookup in propertyLookupList:
            propName=propertyLookup['prop']
            name=propertyLookup['name']
            ask+="|?%s=%s\n" % (propName,name)
        ask+="}}"
        return ask

    @classmethod
    def getJsonFile(cls,entityName):
        '''
        get the json File for the given entityName
        '''
        cachePath=OpenResearch.getCachePath()
        os.makedirs(cachePath,exist_ok=True)
        jsonPrefix="%s/%s" % (cachePath,entityName)
        jsonFilePath="%s.json" % jsonPrefix
        return jsonFilePath

    def fromCache(self,wikiuser:WikiUser,force=False):
        '''
        Args:
            wikiuser: the wikiuser to use
        '''
        jsonFilePath=OREntityList.getJsonFile(self.getEntityName())
        # TODO: fix upstream pyLodStorage
        jsonPrefix=jsonFilePath.replace(".json","")
        if os.path.isfile(jsonFilePath) and not force:
            self.restoreFromJsonFile(jsonPrefix)
        else:
            self.fromWiki(wikiuser,askExtra=self.askExtra,profile=self.profile)
            self.storeToJsonFile(jsonPrefix)

    def toCache(self):
        '''
        store my content to the cache
        '''
        jsonFilePath = OREntityList.getJsonFile(self.getEntityName())
        jsonPrefix = jsonFilePath.replace(".json", "")
        self.storeToJsonFile(jsonPrefix)

    def fromWiki(self,wikiuser:WikiUser,askExtra="",profile=False):
        '''
        read me from a wiki using the given WikiUser configuration
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
        '''
        reaad me from the given sqlTable
        '''
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
                # TODO callBacks should be more generic (if any)
                #if hasattr(entity,"fixRecord"):
                #    fixRecord=getattr(entity,'fixRecord');
                #    if callable(fixRecord):
                #        fixRecord(record)
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

    def fromWikiFileManager(self,wikiFileManager):
        """
        initialize me from the given WikiFileManager
        """
        self.wikiFileManager= wikiFileManager
        wikiFileDict=wikiFileManager.getAllWikiFiles()
        self.fromWikiFiles(wikiFileDict.values())
        
    def fromWikiFiles(self,wikiFileList:list):
        '''
        initialize me from the given list of wiki files
        '''
        templateName=self.clazz.templateName
        wikiSonLod=WikiFileManager.convertWikiFilesToLOD(wikiFileList,templateName)
        lod=self.normalizeLodFromWikiSonToLod(wikiSonLod)
        self.fromLoD(lod)
        
    @classmethod    
    def getPropertyLookup(cls)->dict:
        '''
        get my PropertyLookupList as a map 
        
        Returns:
            dict: my mapping from wiki property names to LoD attribute Names or None if no mapping is defined
        '''
        lookup=None
        if 'propertyLookupList' in cls.__dict__:
            propertyLookupList=cls.__dict__['propertyLookupList']
            lookup,_duplicates=LOD.getLookup(propertyLookupList, 'prop')
        return lookup
      
    def fromSampleWikiSonLod(self,entityClass):
        '''
        get a list of dicts derived form the wikiSonSamples
        
        Returns:
            list: a list of dicts for my sampleWikiText in WikiSon notation
        '''
        wikiFileList=[]
        for sampleWikiText in entityClass.getSampleWikiTextList():
            pageTitle=None
            wikiFile=WikiFile(name=pageTitle,wikiText=sampleWikiText)
            wikiFileList.append(wikiFile)
        self.fromWikiFiles(wikiFileList)

    @classmethod
    def normalizeLodFromWikiSonToLod(cls, wikiSonRecords:list)->list:
        '''
        normalize the given LOD to the properties in the propertyLookupList
        
        Args:
            wikiSonRecords(list): the list of dicts to normalize/convert
            
        Return:
            list: a list of dict to retrieve entities from
        '''
        lookup=cls.getPropertyLookup()
        lod=[]
        if lookup is not None:
            # convert all my records (in place)
            for record in wikiSonRecords:
                if not isinstance(record, dict):
                    continue
                normalizedDict=OREntity.fromWikiSonToLod(record,lookup)
                lod.append(normalizedDict)
        return lod

    def getLoD(self):
        """
        Return the LoD of the entities in the list
        """
        LoD= []
        for entity in self.getList():
            LoD.append(entity.__dict__)
        return LoD


    def getRatedLod(self,ratingCallback=None):
        '''
        get the list of dicts with a potential rating

        Args:
            ratingCallback(func): a function to be called for rating of this entity

        Returns:
            list: a list of dicts with the rating
        '''
        lod=[]
        errors=[]
        for entity in self.getList():
            entityRecord=OrderedDict()
            # default attributes
            for attr in ['pageTitle','lastEditor','creationDate','modificationDate']:
                if hasattr(entity,attr):
                    entityRecord[attr]=getattr(entity,attr)
            for propertyLookup in self.propertyLookupList:
                name=propertyLookup['name']
                if hasattr(entity,name):
                    entityRecord[name]=getattr(entity,name)
            if ratingCallback is not None:
                ratingErrors=ratingCallback(entity,entityRecord)
                if len(ratingErrors)>0:
                    errors.append(ratingErrors)
            lod.append(entityRecord)
        return lod,errors

class EventSeriesList(OREntityList):
    '''
    i represent a list of EventSeries
    '''
    propertyLookupList=[
            { 'prop':'EventSeries acronym', 'name': 'acronym',      'label': 'Acronym'},
            { 'prop':'DblpSeries',          'name': 'dblpSeries',   'label': 'DblpSeries'},
            { 'prop':'Homepage',            'name': 'homepage',     'label': 'Homepage'},
            { 'prop':'Logo',                'name': 'logo',         'label': 'Logo'},
            { 'prop':'Title',               'name': 'title',        'label': 'Title'},
            # TODO enable and handle
            #{ 'prop':'Field',      'name': 'subject'},
            { 'prop':'Wikidataid',          'name': 'wikidataId',   'label': 'WikiDataId'},
            { 'prop':'WikiCfpSeries',       'name': 'wikiCfpSeries','label': 'WikiCfpSeries'},
            { 'prop':'Period',              'name': 'period',       'label': 'Period'},
            { 'prop':'Unit',                'name': 'unit',         'label': 'Unit'},
            { 'prop':'Has CORE Rank',       'name': 'core2018Rank', 'label': 'has CORE2018 Rank'}
            # TODO add more fields according to
            # https://confident.dbis.rwth-aachen.de/or/index.php?title=Template:Event_series&action=edit
    ]
    
    def __init__(self):
        '''
        construct me
        '''
        self.eventSeries=[]
        super(EventSeriesList, self).__init__("eventSeries",EventSeries)
        
class EventSeries(OREntity):
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
            { 'prop':'Acronym',             'name': 'acronym',         "label": "Acronym"},
            { 'prop':'End date',            'name': 'endDate',         "label": "End date"},
            { 'prop':'Event in series',     'name': 'inEventSeries',   "label": "Series"},
            { 'prop':'Event presence',      'name': 'presence',        "label": "presence"},
            { 'prop':'Event type',          'name': 'eventType',       "label": "Type"},
            { 'prop':'Has_location_country','name': 'country',         "label": "Country"},
            { 'prop':'Has_location_state',  'name': 'region',          "label": "State"},
            { 'prop':'Has_location_city',   'name': 'city',            "label": "City"},
            { 'prop':'Has year',            'name': 'year',            "label": "Year"},   
            { 'prop':'Homepage',            'name': 'homepage',        "label": "Homepage"},
            { 'prop':'Ordinal',             'name': 'ordinal',         "label": "Ordinal"},
            { 'prop':'Start date',          'name': 'startDate',       "label": "Start date"},
            { 'prop':'Title',               'name': 'title',           "label": "Title"},
            { 'prop':'Accepted papers',     'name': 'acceptedPapers',  "label": "Accepted papers"},
            { 'prop':'Submitted papers',    'name': 'submittedPapers', "label": "Submitted papers"}
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
            "creationDate": datetime.fromisoformat("2016-09-25T07:36:02"),
            "endDate": datetime.fromisoformat("2017-06-09T00:00:00"),
            "eventType": "Conference",
            "homepage": "http://5guconference.org/2017/show/cf-papers",
            "inEventSeries": "5GU",
            "lastEditor": "Wolfgang Fahl",
            "modificationDate": datetime.fromisoformat("2020-11-05T12:33:23"),
            "ordinal": 2,
            "pageTitle": "5GU 2017",
            "startDate": datetime.fromisoformat("2017-06-08T00:00:00"),
            "title": "2nd EAI International Conference on 5G for Ubiquitous Connectivity"
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
    
class CountryList(OREntityList):
    '''
    a list of countries
    '''
    def __init__(self):
        self.countries=[]
        super(CountryList, self).__init__("countries",Country)
        
        self.propertyLookupList=[
            { 'prop':'Country name',    'name': 'name'},
            { 'prop':'Country wikidatid', 'name': 'wikidataId'}
        ]       
        
    def getDefault(self):
        jsonFilePrefix="%s/orCountries" % OpenResearch.getResourcePath()
        self.restoreFromJsonFile(jsonFilePrefix)

    @classmethod
    def getPluralname(cls):
        return "Countries" 
    
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
    