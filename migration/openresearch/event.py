'''
Created on 2021-04-06

@author: wf
'''
from lodstorage.jsonable import JSONAble,JSONAbleList
from collections import OrderedDict
from datetime import datetime
from wikibot.wikiuser import WikiUser
from wikibot.wikiclient import WikiClient
from wikibot.wikipush import WikiPush
from ormigrate.fixer import PageFixer
from ormigrate.toolbox import HelperFunctions as hf
from wikifile.wikiFileManager import WikiFileManager
from wikifile.wikiFile import WikiFile
from wikifile.wikiRender import WikiRender
import inspect
import os
import time
import ntpath
from pathlib import Path
from openresearch.openresearch import OpenResearch

from ormigrate.issue41 import AcronymLengthFixer
from ormigrate.issue119_Ordinals import OrdinalFixer
from ormigrate.issue71 import DateFixer
from ormigrate.eventSeriesFixer import EventSeriesProvenanceFixer, EventSeriesTitleFixer
from ormigrate.issue152 import AcceptanceRateFixer
from ormigrate.issue170_curation import CurationQualityChecker
from ormigrate.issue195 import BiblographicFieldFixer


class OREntity(JSONAble):
    def __init__(self):
        '''
        Constructor
        '''


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

    def getLookup(self,attrName:str,withDuplicates:bool=False):
        '''
        create a lookup dictionary by the given attribute name

        Args:
            attrName(str): the attribute to lookup
            withDuplicates(bool): whether to retain single values or lists

        Return:
            a dictionary for lookup
        '''
        lookup={}
        duplicates=[]
        for entity in self.getList():
            if hasattr(entity, attrName):
                value=getattr(entity,attrName)
                if value in lookup:
                    if withDuplicates:
                        lookupResult=lookup[value]
                        lookupResult.append(entity)
                    else:
                        duplicates.append(entity)
                else:
                    if withDuplicates:
                        lookupResult=[entity]
                    else:
                        lookupResult=entity
                lookup[value]=lookupResult
        if withDuplicates:
            return lookup
        else:
            return lookup,duplicates

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
|?_CDAT=creationDate
|?_MDAT=modificationDate
|?_LEDT=lastEditor
""" % (selector,askExtra)
        if propertyLookupList is None:
            propertyLookupList=self.propertyLookupList
        for propertyLookup in propertyLookupList:
            propName=propertyLookup['prop']
            name=propertyLookup['name']
            ask+="|?%s=%s\n" % (propName,name)
        ask+="}}"
        return ask

    def getJsonFile(self):
        '''
        get the json File for me
        '''
        cachePath=OpenResearch.getCachePath()
        os.makedirs(cachePath,exist_ok=True)
        jsonPrefix="%s/%s" % (cachePath,self.getEntityName())
        jsonFilePath="%s.json" % jsonPrefix
        return jsonFilePath

    def fromCache(self,wikiuser:WikiUser,force=False):
        '''
        Args:
            wikiuser: the wikiuser to use
        '''
        jsonFilePath=self.getJsonFile()
        # TODO: fix upstream pyLodStorage
        jsonPrefix=jsonFilePath.replace(".json","")
        if os.path.isfile(jsonFilePath) and not force:
            self.restoreFromJsonFile(jsonPrefix)
        else:
            self.fromWiki(wikiuser,askExtra=self.askExtra,profile=self.profile)
            self.storeToJsonFile(jsonPrefix)

    def toCache(self):
        jsonFilePath = self.getJsonFile()
        jsonPrefix = jsonFilePath.replace(".json", "")
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


    def fromWikiSonBackupFiles(self,wikiSonName,backupdir=str(Path.home() / 'wikibackup'/ 'or' ),wikiId= 'or',listOfItems=[]):
        """
        Create me from the backup wiki files of OR Entity

        """
        filepaths = list(hf.absoluteFilePaths(backupdir))
        wikiRender = WikiRender()
        wikiFileList=[]
        for file in filepaths:
            filename = ntpath.basename(file).replace('.wiki','')
            filepath = ntpath.dirname(file)
            if len(listOfItems) > 0:
                if filename in listOfItems:
                    wikiFile = WikiFile(filename, filepath, wikiRender)
                    wikiFileList.append(wikiFile)
            else:
                wikiFile = WikiFile(filename,filepath,wikiRender)
                wikiFileList.append(wikiFile)
        wikiFileManger= WikiFileManager(wikiId)
        LOD=wikiFileManger.convertWikiFilesToLOD(wikiFileList,wikiSonName)
        self.fromLoD(LOD)

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
    def __init__(self):
        self.eventSeries=[]
        super(EventSeriesList, self).__init__("eventSeries",EventSeries)
        self.propertyLookupList=[
            { 'prop':'EventSeries acronym', 'name': 'acronym'},
            { 'prop':'Homepage',   'name': 'homepage'},
            { 'prop':'Title',      'name': 'title'},
            #{ 'prop':'Field',      'name': 'subject'},
            { 'prop':'Wikidataid',  'name': 'wikidataId'},
            { 'prop':'DblpSeries',  'name': 'dblpSeries' }
        ]
        
class EventSeries(OREntity):
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
            'title' : 'Conference on Artificial Intelligence',
            'subject' : 'Artificial Intelligence',
            'homepage' : 'www.aaai.org/Conferences/AAAI/aaai.php',
            'wikidataId' : 'Q56682083',
            'dblpSeries' : 'aaai'
        },
        {
            "acronym": "3DUI",
            "creationDate": datetime.fromisoformat("2020-03-17T22:54:10"),
            "dblpSeries": "3dui",
            "lastEditor": "Wolfgang Fahl",
            "modificationDate": datetime.fromisoformat("2021-02-13T06:56:46"),
            "pageTitle": "3DUI",
            "title": "IEEE Symposium on 3D User Interfaces",
            "wikidataId": "Q105456162"
        },]
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
    
    @classmethod       
    def rateMigration(cls,eventSeries,eventSeriesRecord):
        '''
        get the ratings from the different fixers
        '''
        pageFixerList= [
            {
                "column": "provenancePainRating",
                "fixer": EventSeriesProvenanceFixer
            },
            {
                "column": "curationPainRating",
                "fixer": CurationQualityChecker
            },
            {
                "column": "titlePainRating",
                "fixer": EventSeriesTitleFixer
            }
        ]
        return PageFixer.rateWithFixers(pageFixerList, eventSeries,eventSeriesRecord)
        
    
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
        self.propertyLookupList=[
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



class Event(OREntity):
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
}}""","""{{Event
|Acronym=AISB 2009
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
    

            
    @classmethod       
    def rateMigration(cls,event,eventRecord):
        '''
        get the ratings from the different fixers
        '''
        pageFixerList= [
            {
                "column": "curationPainRating",
                "fixer": CurationQualityChecker
            },
            {
                "column": "acronymPainRating",
                "fixer": AcronymLengthFixer
            },
            {
                "column": "ordinalPainRating",
                "fixer": OrdinalFixer
            },
            {
                "column": "datePainRating",
                "fixer": DateFixer
            },
            {
                "column": "AcceptanceRatePainRating",
                "fixer": AcceptanceRateFixer
            },
            {
                "column": "BiblographicFieldFixer",
                "fixer": BiblographicFieldFixer
            }
        ]
        return PageFixer.rateWithFixers(pageFixerList, event,eventRecord)
    
    def __str__(self):
        text=self.pageTitle
        if hasattr(self, "acronym"):
            text+="(%s)" %self.acronym
        return text
    
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
    