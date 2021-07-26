from geograpy.locator import LocationContext, Location, City, Country, Region
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer
from ormigrate.smw.rating import Rating, RatingType, EntityRating


class LocationFixer(ORFixer):
    '''
    see purpose and issue
    '''
    purpose="fixes Locations"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/220"
    
    # value of type attribute of Locations to be fixed
    COUNTRY = "country"
    REGION = "region"
    CITY = "city"

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(LocationFixer, self).__init__(pageFixerManager)
        LocationFixer.locationContext=self.getORLocationContext()

    def fix(self,rating:EntityRating):
        '''
        tries fixing the location entries of the  given entity
        '''
        eventRecord = rating.getRecord()
        self.fixEventRecord(eventRecord)

    def fixEventRecord(self, event:dict, errors:dict=None, bestFit=True):
        '''
        Args:
            event(dict): event records containing the location values that should be fixed
            errors(dict): dictonary containing the errors of the given event record → new errors are added to the dict
            bestFit(bool): If true the best/closed fit for a location is chosen (e.g. city with highest population). Otherwise a fix is only applied if the location can be identified with certainty.
        '''
        # event location values
        if errors is None:
            errors = {}
        event_city = event[self.CITY] if self.CITY in event and event[self.CITY] != "" else None
        event_region = event[self.REGION] if self.REGION in event and event[self.REGION] != "" else None
        event_country = event[self.COUNTRY] if self.COUNTRY in event and event[self.COUNTRY] != "" else None
        # filter out known invalid and None values
        if event_country in ["Online", "None", "N/A"]:
            event_country=None
        if event_region in ["Online", "None", "N/A"]:
            event_region=None
        if event_city in ["Online", "None", "N/A"]:
            event_city=None
        cities = self.locationContext.getCities(event_city)
        regions = self.locationContext.getRegions(event_region)
        countries = self.locationContext.getCountries(event_country)
        if event_city is None:
            missing_city=True
            errors["city_missing"]="city entry missing"
        else:
            if not cities:
                errors["city_unrecognized"]=f"City '{event_city}' not found in LocationCorpus"
        if event_region is None:
            missing_region=True
            errors["region_missing"] = "region entry missing"
        else:
            if not regions:
                errors["region_unrecognized"] = f"Region '{event_region}' not found in LocationCorpus"
        if event_country is None:
            missing_country=True
            errors["country_missing"] = "country entry missing"
        else:
            if not countries:
                errors["country_unrecognized"] = f"Country '{event_country}' not found in LocationCorpus"

        if event_region == "Washington" and event_city == "Washington":
            print("Washington")
        isPossiblyMisplaced=False
        if event_city is not None:
            # event has city
            if cities:
                # event_city matches cities in locationCorpus -> check if identifiable
                if regions:
                    # filter those cities out for which the defined region is not found in any city
                    regionids = self.getWikidataIds(regions)
                    cities = list(filter(
                        lambda x: 'wikidataid' in x.region.__dict__ and x.region.wikidataid in regionids,
                                  cities))
                    countries = list(filter(
                        lambda x: 'wikidataid' in x.country.__dict__ and x.country.wikidataid in regionids,
                        cities))
                if countries:
                    # filter those cities out for which the defined country is not found in any city
                    countryids=self.getWikidataIds(countries)
                    cities = list(filter(
                        lambda x: 'wikidataid' in x.country.__dict__ and x.country.wikidataid in countryids,
                        cities))
                if len(cities) >0:
                    # city can be identified (Could still be incorrect)
                    if len(cities) > 1:
                        errors["city_unclear"] = f"City '{event_city}' matches against multiple cities in the LocationCorpus. Other location information are not sufficient enough to clearly identify the city"
                        cities=sorted(cities,key=lambda city:0 if 'population'not in city.__dict__ or city.population is None else int(city.population), reverse=True)
                    final_city = cities[0]
                    if isinstance(final_city,City):
                        event[self.CITY]=self.getPageTitle(final_city)
                        event[self.REGION] = self.getPageTitle(final_city.region)
                        event[self.COUNTRY] = self.getPageTitle(final_city.country)
                        errors["complete"]="Location of event complete"
                        return event, errors
                else:
                    # No matching city -> Two possibilities: event location information incorrect or locations missing in LocationCorpus
                    errors["city_unknown"]=f"City '{event_city}' could not be matched against a city in the LocationCorpus with the given region and country. Either location information are incorrect or location is missing in the corpus."
                    #return None, errors
            else:
                # event_city is not the LocationCorpus
                isPossiblyMisplaced=True
        if event_region is not None:
            # event_city is not defined
            if regions:
                if countries:
                    # filter those cities out for which the defined country is not found in any city
                    countryids=self.getWikidataIds(countries)
                    regions = list(filter(
                        lambda x: 'wikidataid' in x.country.__dict__ and x.country.wikidataid in countryids,
                        regions))
                if len(regions)==1:
                    # region can be identified
                    final_region = regions[0]
                    if isinstance(final_region, Region):
                        event[self.REGION] = self.getPageTitle(final_region)
                        event[self.COUNTRY] = self.getPageTitle(final_region.country)
                        return event, errors
                elif len(regions) == 0:
                    # No matching region -> Two possibilities: event location information incorrect or locations missing in LocationCorpus
                    errors["region_unknown"]=f"Region '{event_region}' could not be matched against a region in the LocationCorpus with the given country. Either location information are incorrect or location is missing in the corpus."
                    #return None, errors
                else:
                    errors["region_unclear"]=f"Region '{event_region}' matches against multiple regions in the LocationCorpus. Other location information are not sufficient enough to clearly identify the region"
            else:
                isPossiblyMisplaced = True
                pass
        if event_country is not None:
            if countries:
                if len(countries)==1:
                    final_country=countries[0]
                    event[self.COUNTRY] = self.getPageTitle(final_country)
                    return event, errors
                elif len(countries) == 0:
                    # No matching region -> Two possibilities: event location information incorrect or locations missing in LocationCorpus
                    errors["country_unknown"]=f"Country '{event_country}' could not be matched against a country in the LocationCorpus with the given country. Either location information are incorrect or location is missing in the corpus."
                    #return None, errors
                else:
                    errors["country_unclear"] = f"Country '{event_region}' matches against multiple country in the LocationCorpus. Other location information are not sufficient enough to clearly identify the region"
            else:
                isPossiblyMisplaced = True
                pass
        # event locations could not be matched could not be
        #ToDo: Extend the tests for the location position changes to avoid unnecessary changes
        if isPossiblyMisplaced:
            changed_positions=self.fixLocationType(event)
            if changed_positions:
                return self.fixEventRecord(event)
        return None,errors

    def fixLocationType(self, event:dict):
        """
        Tries to rearrange the location entries of the given event if possible to fix miss placed information.
        Does not overwrite correctly recognized entries.
        Note: Should be used with care
        E.g.: City=Bavaria will be changed to State=Bavaria

        Args:
            event(dict): Event dict that should be checked/fixed

        Returns:
            True if location entries were rearranged. Otherwise false
        """
        event_city=event.get(self.CITY)
        event_region=event.get(self.REGION)
        event_country=event.get(self.COUNTRY)
        cities = self.locationContext.getCities(event_city)
        regions = self.locationContext.getRegions(event_region)
        countries = self.locationContext.getCountries(event_country)
        modified_city=False
        modified_region=False
        modified_country=False
        # check city
        if event_city is not None:
            possible_regions=self.locationContext.getRegions(event_city)
            possible_country=self.locationContext.getCountries(event_city)
            if possible_regions and possible_country:
                # city could be region or country -> undecidable
                pass
            elif possible_regions and not regions:
                event[self.REGION]=event_city
                modified_region=True
                if not modified_city:
                    del event[self.CITY]
            elif possible_country and not countries:
                event[self.COUNTRY]=event_city
                modified_country=True
                if not modified_city:
                    del event[self.CITY]
        if event_region is not None:
            possible_cities=self.locationContext.getCities(event_region)
            possible_country=self.locationContext.getCountries(event_region)
            if possible_cities and possible_country:
                # region could be city or country -> undecidable
                pass
            elif possible_cities and not cities:
                event[self.CITY]=event_region
                modified_city=True
                if not modified_region:
                    del event[self.REGION]
            elif possible_country and not countries:
                event[self.COUNTRY]=event_region
                modified_country=True
                if not modified_region:
                    del event[self.REGION]
        if event_country is not None:
            possible_cities=self.locationContext.getCities(event_country)
            possible_regions=self.locationContext.getRegions(event_country)
            if possible_cities and possible_regions:
                # country could be city or region -> undecidable
                pass
            elif (possible_cities and not cities) or (possible_cities and modified_country):
                event[self.CITY]=event_country
                modified_city=True
                if not modified_country:
                    del event[self.COUNTRY]
            elif (possible_regions and not regions) or (possible_cities and modified_country):
                event[self.REGION] = event_country
                modified_region=True
                if not modified_country:
                    del event[self.COUNTRY]
        return modified_city or modified_region or modified_country

    @staticmethod
    def getWikidataIds(locations: list):
        '''
        Returns a set of wikidataids of the given locations

        Args:
            locations(list): list of Locations

        Returns:
            List of wikidata ids from the locations of the given list
        '''
        res = {x.wikidataid for x in locations if 'wikidataid' in x.__dict__}
        return res

    @staticmethod
    def getPageTitle(location:Location):
        '''
        Returns the wiki page title for the given location
        The hierarchy of the location is hereby represented in the page title
        The page titles are constructed as follows:
            -Countries: country_isocode     e.g. US
            -Regions: country_isocode/region_isocode    e.g US/CA
            -Cities: country_isocode/region_isocode/city_name   e.g. US/CA/Los_Angeles

        Args:
            location(Location): location for which the corresponding wiki pageTitle should be returned

        Returns:
            wiki pageTitle of the given location as string
        '''
        pageTitle=None
        if isinstance(location, City):
            if 'name' in location.__dict__:
                nameCity=location.__dict__.get('name')
                isoParts=nameCity.split("-")
                isoRegion = LocationFixer.getPageTitle(location.region)
                if isoRegion is not None:
                    pageTitle=f"{isoRegion}/{nameCity}"
                else:
                    pageTitle=None
        elif isinstance(location, Region):
            if 'iso' in location.__dict__:
                isoRegion=location.__dict__.get('iso')
                isoParts=isoRegion.split("-")
                isoCountry = LocationFixer.getPageTitle(location.country)
                if len(isoParts) == 2:
                    # assumed iso format of regions US-CA
                    isoRegion=isoParts[1]
                    if isoCountry is None:
                        isoCountry=isoParts[0]
                    pageTitle=f"{isoCountry}/{isoRegion}"
                else:
                    pageTitle=None
        elif isinstance(location, Country):
            if 'iso' in location.__dict__:
                pageTitle=location.__dict__.get('iso')
        else:
            pageTitle=location.name
        return pageTitle


    def rate(self, rating:EntityRating):
        '''
        get the pain Rating for the given eventRecord
        '''
        eventRecord=rating.getRecord()
        arating=self.getRating(eventRecord)
        rating.set(arating.pain, arating.reason, arating.hint)

    @classmethod
    def getRating(cls, eventRecord):
        painrating = None
        city = None
        region = None
        country = None

        if cls.CITY in eventRecord: city = eventRecord[cls.CITY]
        if cls.REGION in eventRecord: region = eventRecord[cls.REGION]
        if cls.COUNTRY in eventRecord: country = eventRecord[cls.COUNTRY]
        if not city and not region and not country:
            # location is not defined
            painrating=Rating(7, RatingType.missing,f'Locations are not defined')
        else:
            if 'locationContext' in cls.__dict__:
                cities=cls.__dict__['locationContext'].getCities(city)
                regions=cls.__dict__['locationContext'].getCities(region)
                countries=cls.__dict__['locationContext'].getCities(country)
            if cities and regions and countries:
                # all locations are recognized
                painrating=Rating(1,RatingType.ok,f'Locations are valid. (Country: {country}, Region: {region}, City:{city})')
            elif not cities:
                # City is not valid
                painrating=Rating(6, RatingType.invalid,f'City is not recognized. (City:{city})')
            elif not regions:
                # City is valid but region is not
                painrating=Rating(5, RatingType.invalid,f'Region is not recognized. (Country: {country}, Region: {region}, City:{city})')
            else:
                # City and region are valid but country is not
                painrating=Rating(3, RatingType.invalid,f'Country is not recognized. (Country: {country}, Region: {region}, City:{city})')
        return painrating

    @staticmethod
    def getORLocationContext():
        '''
        Returns a LocationContext enhanced with location labels used by OPENRESEARCH
        '''
        locationContext = LocationContext.fromJSONBackup()
        if locationContext is None:
            return
        for locations in locationContext.countries, locationContext.regions, locationContext.cities:
            for location in locations:
                LocationFixer._addPageTitleToLabels((location))
                LocationFixer._addCommonNamesToLabels((location))
        return locationContext

    @staticmethod
    def _addPageTitleToLabels(location: Location):
        '''
        Adds the pageTitle of the given location to the labels of the given location
        '''
        pageTitle = LocationFixer.getPageTitle(location)
        LocationFixer._addLabelToLocation(location, pageTitle)

    @staticmethod
    def _addCommonNamesToLabels(location: Location):
        '''
        Add commonly used names to the labels
        '''
        if isinstance(location, Country):
            label = f"Category:{location.name}"
            LocationFixer._addLabelToLocation(location, label)

    @staticmethod
    def _addLabelToLocation(location: Location, *label: str):
        '''
        Adds the given labels to the given location
        '''
        for l in label:
            if 'labels' in location.__dict__:
                labels = location.__dict__['labels']
                if isinstance(labels, list):
                    labels.append(l)
                else:
                    labels = [l, labels]
                location.__dict__['labels'] = labels
            else:
                location.__dict__['labels'] = [l]
    
if __name__ == '__main__':
    PageFixerManager.runCmdLine([LocationFixer])