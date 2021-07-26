from geograpy.locator import LocationContext, Location, City, Country, Region
from ormigrate.issue220_location import LocationFixer
from wikifile.wikiFileManager import WikiFileManager
from ormigrate.fixer import PageFixerManager
from wikifile.wikiFile import WikiFile
from collections import Counter
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
        self.locationContext = self.locationFixer.getORLocationContext()

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



    def generateORLocationPages(self, events:list, overwrite:bool=False, limit:int=None):
        '''

        Args:
            events(list): List of events for which the needed Location pages are generated
            overwrite(bool): If False the generated page is only saved if the page already exists. Otherwise save the file even if it does not exist already.
            limit(bool): Number of most used cities for which the cities and regions should be generated. Does not affect the generated countries. If None generate city and region for all used cities.
        '''
        # Generate country location pages
        self.generateLocationPages(self.locationContext.countries, overwrite)
        # Fix locations of the event → Normalized location names afterwards
        for event in events:
            self.locationFixer.fixEventRecord(event.__dict__)

        cityCounter=EventLocationHandler.getFieldCounter(events, 'city', 'City')
        usedCities=[]
        if limit is None:
            usedCities=cityCounter.keys()
        else:
            # limit used cities to the cities that are most used
            usedCities=[city for (city, counter) in cityCounter.most_common(limit)]
        regions = set()   # Regions used by the cities in usedCities
        # Generate city location page if city is recognized and add region of the city to regions
        for cityName in usedCities:
            possibleCities=self.locationContext.getCities(cityName)
            if possibleCities is None or possibleCities == []:
                print(f"City {cityName} not recognized by LocationContext")
                pass
            else:
                location=max(possibleCities, key=lambda city: int(city.population) if 'population' in city.__dict__ and city.population is not None else 0)
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
            overwrite(bool): If False the generated page is only saved if the page already exists. Otherwise save the file even if it does not exist already.
        '''
        pageTitle = LocationFixer.getPageTitle(location)
        wikiFile = WikiFile(name=pageTitle, wikiText="", wikiFileManager=self.wikiFileManager)
        locationFields = LOD.getFields(self.getSamples())
        locationData = {}
        for field in locationFields:
            if field in location.__dict__:
                locationData[field] = location.__dict__[field]
            if field == "coordinates":
                lat = location.__dict__.get('lat')
                lon = location.__dict__.get('lon')
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

    @staticmethod
    def getFieldCounter(lod: list, *field:str):
        '''
        Count number of occurrences of the values of the given fields in the given list
        ToDo: Propose migration to pyLODStorage.LOD
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

