import json
import os
import sys
from collections import Counter

from corpus.lookup import CorpusLookup
from wikifile.metamodel import Topic
from wikifile.wikiRender import WikiRender

from openresearch.openresearch import OpenResearch
from geograpy.locator import Location, City, Country, Region
from wikifile.cmdline import CmdLineAble
from ormigrate.issue220_location import LocationFixer
from wikifile.wikiFileManager import WikiFileManager
from ormigrate.fixer import PageFixerManager
from wikifile.wikiFile import WikiFile
from lodstorage.lod import LOD


class EventLocationHandler(object):
    '''
    Extends the geograpy3 LocationContext with methods required to fix the events and location entries in OPENRESEARCH
    '''

    def __init__(self, wikiFileManager:WikiFileManager):
        '''
        Initalize the object by creating a LocationContext and enhancing it with the openresearch location nameing
        convention (or names assigned as label to each location)
        '''
        self.wikiFileManager=wikiFileManager
        pageFixerManager=PageFixerManager([LocationFixer],wikiFileManager)
        self.locationFixer=LocationFixer(pageFixerManager)
        self.locationContext = OpenResearch.getORLocationContext()
        self.locationContext.countryManager.fromCache()

    def getSamples(self)->list:
        '''
        Returns samples of EventLocationContext class describing the attributes which an be expected
        '''
        samples=[
            {
                "name" : "America",
                "wikidataid" : "Q828",
                "level" : 1,
                "coordinates" : "20, 100",
                "locationKind" : "Continent",
                "partOf" : "Category:World",
                "zoomLevel" : 1
            }
        ]
        return samples



    def generateORLocationPages(self, events:list, overwrite:bool=False, fixLocation=False, limit:int=10):
        '''

        Args:
            events(list): List of events for which the needed Location pages are generated
            overwrite(bool): If False the generated page is only saved if the page already exists. Otherwise save the file even if it does not exist already.
            limit(bool): limit generation of city pages to n-th deciles
        '''
        # Generate country location pages
        self.generateLocationPages(self.locationContext.countries, overwrite)
        # Fix locations of the event → Normalized location names afterwards
        if fixLocation:
            for event in events:
                self.locationFixer.fixEventRecord(event.__dict__)

        usedCities=self.getNthCityDecile(events, limit)
        usedCities=[c for c in usedCities if c not in ["Online", "None", "N/A", "", None]]
        regions = set()   # Regions used by the cities in usedCities
        # Generate city location page if city is recognized and add region of the city to regions
        for cityName in usedCities:
            if cityName is None:
                continue
            possibleCities=self.locationContext.cityManager.getByName(*cityName.split('/'))
            if possibleCities is None or possibleCities == []:
                print(f"City {cityName} not recognized by LocationContext")
                pass
            else:
                location=max(possibleCities, key=lambda city: int(city.pop) if hasattr(city,'pop') and getattr(city, "pop") else 0)
                if location:
                    regions.add(location.region)
                    self.generateLocationPage(location, overwrite)
        # Generate region pages
        for region in regions:
            self.generateLocationPage(region, overwrite)

    def generateLocationPages(self, data:list,overwrite:bool=False):
        '''
        Generates for the given list of locations the corresponding location wiki pages and saves it under the given path.

        Args:
            data(list): List of Locations for which the pages should be generated
            overwrite(bool): If False the generated page is only saved if the page already exists. Otherwise save the file even if it does not exist already.
        '''
        for location in data:
            self.generateLocationPage(location, overwrite)


    def generateLocationPage(self, location:Location, overwrite:bool=False):
        '''
        Generates the wiki page corresponding to the given location and saves it under the given path.

        Args:
            location(Location): Location for which the page should be generated
            overwrite(bool): If False the generated page is only saved if the page does not already exists. Otherwise generated files might overwrite existing files.
        '''
        pageTitle = LocationFixer.getPageTitle(location)
        wikiFile = WikiFile(name=pageTitle, wikiText="", wikiFileManager=self.wikiFileManager)
        locationFields = LOD.getFields(self.getSamples())
        locationData = {}
        for field in locationFields:
            if field in location.__dict__:
                locationData[field] = getattr(location, field)
            if field == "coordinates":
                lat = getattr(location,'lat')
                lon = getattr(location,'lon')
                if lat and lon:
                    locationData[field] = f"{lat},{lon}"
            elif field == "partOf":
                partOf = ''
                if isinstance(location, Country):
                    partOf = ''
                elif isinstance(location, Region):
                    partOf = location.country.iso
                elif isinstance(location, City):
                    partOf = location.region.iso.replace('-', '/')
                locationData[field] = partOf
        wikiFile.add_template(template_name="Location", data=locationData)
        wikiFile.save_to_file(overwrite=overwrite)


    def getNthCityDecile(self, events:list, n:int=10):
        '''
        Returns the cities of the n-th decile

        Args:
         events(list): List of event records which should be considered for the calculation of the decile
         n: n-th decile of used cities to return

        Returns:
         List of city names in requested decile
        '''
        cityNames=[getattr(record,self.locationFixer.CITY) for record in events]
        counter=Counter(cityNames)
        target=n*0.1*len(events)
        sum=0
        nthDecile=[]
        for (name, counter) in counter.most_common():
            if sum>=target:break
            nthDecile.append(name)
            sum+=counter
        return nthDecile


    @staticmethod
    def getFieldCounter(lod: list, *field:str):
        '''
        Count number of occurrences of the values of the given fields in the given list
        Args:
            lod(list): List of dicts of list of objects for which the values fo the given fields should be counted
            field(str): One or more fields for which the number of occurrences of the value should be counted

        Returns:
            Dict which contains the field value as key and number of occurrences as value
        '''
        fieldValues = []
        for record in lod:
            for f in field:
                if isinstance(record, dict):
                    value = record.get(f)
                else:
                    value = record.__dict__.get(f)
                fieldValues.append(value)
        counterList = Counter(fieldValues)
        return counterList

    @staticmethod
    def getTopicFromResources(topicName:str) -> Topic:
        """
        Retrieves the topic and property definitions from the resources anc converts them into a Topic object.
        Args:
            topicName: name of the topic

        Returns:
            Topic
        """
        resources = OpenResearch.getResourcePath()
        topicSpec = None
        with open(f"{resources}/topics/{topicName}.json", mode="r") as f:
            topicSpec = json.load(f)
        locationSpec = {"data": [topicSpec.get("topic")]}
        locationPropertySpec = {"data": topicSpec.get("properties")}
        topic = Topic.from_wiki_json(topic_json=json.dumps(locationSpec),
                                             prop_json=json.dumps(locationPropertySpec))
        return topic

    @staticmethod
    def generateTechnicalPages(topic:str, wikiFileManager:WikiFileManager, overwrite:bool=False, templateParamMapping:dict=None, **templates):
        '''
        Generates the technical pages of the Location topic
        Pages such as Help:Location, List of Lcoations, Concept:Location, ...

        Args:
            overwrite(bool): If False the generated page is only saved if the page does not already exists. Otherwise generated files might overwrite existing files.
        '''
        topic=EventLocationHandler.getTopicFromResources(topic)
        if templateParamMapping:
            topic.templateParamMapping=templateParamMapping
        wikiRender=WikiRender()
        wikiRender.generateTopic(topic, overwrite=overwrite, path=wikiFileManager.targetPath, **templates)


if __name__ == '__main__':
    cmdLine = CmdLineAble()
    cmdLine.getParser()
    cmdLine.parser.add_argument("--decile", default=None, dest="decile",help="decile of cities for which the locations should be generated")
    argv = sys.argv[1:]
    args = cmdLine.parser.parse_args(argv)
    home = os.path.expanduser("~")
    if args.backupPath is None:
        targetWikiTextPath = f"{home}/.or/generated/Location"
    else:
        targetWikiTextPath=args.backupPath
    wikiFileManager = WikiFileManager(sourceWikiId=args.source, wikiTextPath=args.backupPath,targetWikiTextPath=targetWikiTextPath, login=False,debug=args.debug)
    lookupId="orclone-backup"
    def patchEventSource(lookup):
        lookup.getDataSource(lookupId).eventManager.wikiFileManager = wikiFileManager
        lookup.getDataSource(lookupId).eventSeriesManager.wikiFileManager = wikiFileManager
    eventLocationHandler=EventLocationHandler(wikiFileManager)
    # generate technical pages for the location topic
    eventLocationHandler.generateTechnicalPages("location", wikiFileManager, overwrite=True)
    # generate location pages
    lookup = CorpusLookup(lookupIds=[lookupId], configure=patchEventSource)
    lookup.load(forceUpdate=False)
    eventDataSource = lookup.getDataSource(lookupId)
    eventRecords=[e.__dict__ for e in eventDataSource.eventManager.getList()]
    eventLocationHandler.generateORLocationPages(events=eventDataSource.eventManager.getList(), limit=int(args.decile), overwrite=True)