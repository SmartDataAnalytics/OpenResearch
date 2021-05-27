from lodstorage.jsonable import JSONAble,JSONAbleList

from openresearch.openresearch import OpenResearch


class LocationCorpus(object):
    '''Contains the locations as linked objects'''

    def __init__(self):
        self._countryList=CountryList()
        self._regionList=RegionList()
        self._cityList=CityList()
        self.countries=self._countryList.restoreFromJsonFile("%s/countries" % OpenResearch.getResourcePath())
        self.regions=self._regionList.restoreFromJsonFile("%s/regions" % OpenResearch.getResourcePath())
        self.cities=self._cityList.restoreFromJsonFile("%s/cities" % OpenResearch.getResourcePath())
        self._linkRegionsToCountries()
        self._linkCitiesToCountries()
        self._cityLUT=self._getLUT(self.cities)
        self._regionLUT=self._getLUT(self.regions)
        self._countryLUT=self._getLUT(self.countries)

    def save(self):
        pass

    @staticmethod
    def _getLUT(data:list):
        '''Creates a LookUpTable for the given list by setting the name and labels as possible key to find the data items'''
        lut={}
        for record in data:
            labels=set()
            if 'name' in record.__dict__:
                labels.add(record.__dict__['name'])
            if 'labels' in record.__dict__:
                labels.update(record.__dict__['labels'])
            for label in labels:
                if label in lut:
                    lut[label].append(record)
                else:
                    lut[label]=[record]
        return lut

    def _linkRegionsToCountries(self):
        countryLUT={c.isocode.replace('-','/'):c for c in self.countries}
        for region in self.regions:
            if 'partOf' in region.__dict__ and region.partOf in countryLUT:
                region.partOf=countryLUT[region.partOf]
            else:
                print(f"Could not link to any country! Region:{region.toJSON()}")

    def _linkCitiesToCountries(self):
        regionLUT={c.isocode.replace('-','/'):c for c in self.regions}
        for city in self.cities:
            if 'partOf' in city.__dict__ and city.partOf in regionLUT:
                city.partOf=regionLUT[city.partOf]
            else:
                print(f"Could not link to any region! City:{city.toJSON()}")

    def getCountry(self, name):
        '''Returns all countries that are known under the given name that are in this LocationCorpus'''
        if name is None:
            return None
        return self._countryLUT.get(name)

    def getRegion(self, name):
        '''Returns all cities that are known under the given name that are in this LocationCorpus'''
        if name is None:
            return None
        return self._regionLUT.get(name)

    def getCity(self, name):
        '''Returns all cities that are known under the given name that are in this LocationCorpus'''
        if name is None:
            return None
        return self._cityLUT.get(name)

    @staticmethod
    def getLocationByWikidataid(id:str, data:str):
        res = list(filter(lambda x: 'wikidataid' in x.__dict__ and x.wikidataid==id, data))
        if res is None:
            return None
        return res[0]

    @staticmethod
    def getWikidataIds(locations:list):
        """Returns a set of wikidataids of the given locations"""
        res={x.wikidataid for x in locations if 'wikidataid' in x.__dict__}
        return res


class Location(JSONAble):
    '''
    Represents a Location
    '''
    def __init__(self, **kwargs):
        self.__dict__=kwargs

    @classmethod
    def getSamples(cls):
        samplesLOD = [{
            "name": "Los Angeles",
            "wikidataid": "Q65",
            "coordinates": "34.05223,-118.24368",
            "partOf": "US/CA",
            "level": 5,
            "locationKind": "City",
            "comment": None,
            "population": 3976322
        }]
        return samplesLOD

    def getPageTitle(self):
        return self.name

    def addLabel(self, label:str):
        '''Adds the given label to the set of labels'''
        if 'labels' not in self.__dict__:
            self.__dict__['labels']=[]
        self.labels.append(label)

    def isKnownAs(self, name)->bool:
        '''
        Checks if this location is known under the given name

        Args:
            name(str): name the location should be checked against

        Returns:
            True if the given name is either the name of the location or present in the labels of the location
        '''
        isKnown=False
        if 'labels' in self.__dict__:
            if name in self.labels:
                isKnown=True
        if name == self.name:
            isKnown=True
        return isKnown


class Country(Location):

    def __init__(self, **kwargs):
        super(Country, self).__init__(**kwargs)
        if 'level' not in self.__dict__:
            self.__dict__['level']=3
        if 'locationKind' not in self.__dict__:
            self.__dict__['locationKind']="Country"

    @classmethod
    def getSamples(cls):
        samplesLOD = [{
            "name": "United States of America",
            "wikidataid": "Q30",
            "coordinates": "39.82818, -98.5795",
            "partOf": "North America",
            "level": 3,
            "locationKind": "Country",
            "comment": None,
            "labels":["USA", "US", "United States of America"],
            "isocode":"US"
        }]
        return samplesLOD

    def getPageTitle(self):
        '''Returns the page name of this country'''
        if 'isocode' in self.__dict__:
            return self.isocode


class Region(Location):

    def __init__(self, **kwargs):
        super(Region, self).__init__(**kwargs)
        if 'level' not in self.__dict__:
            self.__dict__['level']=4
        if 'locationKind' not in self.__dict__:
            self.__dict__['locationKind']="Region"

    @classmethod
    def getSamples(cls):
        samplesLOD = [{
            "name": "California",
            "wikidataid": "Q99",
            "coordinates": "37.0,-120.0",
            "partOf": "US",
            "level": 4,
            "locationKind": "Region",
            "comment": None,
            "labels": ["CA", "California"],
            "isocode": "US-CA"
        }]
        return samplesLOD

    def getPageTitle(self):
        if 'partOf' in self.__dict__ and 'isocode' in self.__dict__:
            regionIsoCodeSegment=self.isocode.split("-")[1]   #ToDo: Check fi this works for any isocode entry
            if isinstance(self.partOf, Location):
                return f"{self.partOf.getPageTitle()}/{regionIsoCodeSegment}"
            else:
                return f"{self.partOf}/{regionIsoCodeSegment}"
        else:
            print(f"Correct page title could not be generated for {self.toJSON()}")
            return None

    def getCountry(self)->Country:
        '''Returns the country of this region'''
        if 'partOf' in self.__dict__:
            if isinstance(self.partOf, Country):
                return self.partOf
        return None


class City(Location):

    def __init__(self, **kwargs):
        super(City, self).__init__(**kwargs)
        if 'level' not in self.__dict__:
            self.__dict__['level']=5
        if 'locationKind' not in self.__dict__:
            self.__dict__['locationKind']="City"

    @classmethod
    def getSamples(cls):
        samplesLOD = [{
            "name": "Los Angeles",
            "wikidataid": "Q65",
            "coordinates": "34.05223,-118.24368",
            "partOf": "US/CA",
            "level": 5,
            "locationKind": "City",
            "comment": None,
            "population": "3976322"
        }]
        return samplesLOD

    def getPageTitle(self):
        if 'partOf' in self.__dict__ and 'name' in self.__dict__:
            if isinstance(self.partOf, Location):
                return f"{self.partOf.getPageTitle()}/{self.name}"
            else:
                return f"{self.partOf}/{self.name}"
        else:
            print(f"Correct page title could not be generated for {self.toJSON()}")
            return None

    def getRegion(self)->Region:
        '''Returns the Region of the city'''
        if 'partOf' in self.__dict__:
            if isinstance(self.partOf, Region):
                return self.partOf
        return None

    def getCountry(self)->Country:
        '''Returns the country of this city'''
        if 'partOf' in self.__dict__:
            if isinstance(self.partOf, Region):
                return self.partOf.getCountry()
        return None


class LocationList(JSONAbleList):
    
    def __init__(self,listName:str=None,clazz=None,tableName:str=None):
        super(LocationList, self).__init__(listName, clazz, tableName)


class CountryList(LocationList):
    
    def __init__(self):
        super(CountryList, self).__init__('countries', Country)


class RegionList(LocationList):
    
    def __init__(self):
        super(RegionList, self).__init__('regions', Region)


class CityList(LocationList):
    
    def __init__(self):
        super(CityList, self).__init__('cities', City)