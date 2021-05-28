from openresearch.event import EventList, Event
from openresearch.location import LocationCorpus, CityList, City, Region
from ormigrate.fixer import PageFixer, WikiPage

class LocationFixer(PageFixer):
    '''
    fixes Locations
    '''
    COUNTRY = "Country"
    REGION = "State"
    CITY = "City"

    def __init__(self, wikiClient, debug=False):
        '''
        Constructor
        '''
        # call super constructor
        super(LocationFixer, self).__init__(wikiClient)
        self.debug = debug
        self.locationCorpus=LocationCorpus()

    def fixEventRecords(self, events:list, dryRun=True):
        """
        Gets list of dicts (list of events) and tries to fix the location entries
        """
        count=0
        stats={}
        for event_unfixed in events:
            event, errors = self.fixEventRecord(event_unfixed)
            print(errors)
            if errors is not None:
                for error in errors.keys():
                    if error in stats:
                        stats[error]+=1
                    else:
                        stats[error]=1
        print(stats)
        #self.locationCorpus.save()

    def fixEventRecord(self, event:dict, errors=None):
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
        cities = self.locationCorpus.getCity(event_city)
        regions = self.locationCorpus.getRegion(event_region)
        countries = self.locationCorpus.getCountry(event_country)
        if event_city is None:
            missing_city=True
            errors["city_missing"]="city entry missing"
        else:
            if cities is None:
                errors["city_unrecognized"]=f"City '{event_city}' not found in LocationCorpus"
        if event_region is None:
            missing_region=True
            errors["region_missing"] = "region entry missing"
        else:
            if regions is None:
                errors["region_unrecognized"] = f"Region '{event_region}' not found in LocationCorpus"
        if event_country is None:
            missing_country=True
            errors["country_missing"] = "country entry missing"
        else:
            if countries is None:
                errors["country_unrecognized"] = f"Country '{event_country}' not found in LocationCorpus"

        if event_region == "Washington" and event_city == "Washington":
            print("Washington")
        isPossiblyMisplaced=False
        if event_city is not None:
            # event has city
            if cities is not None:
                # event_city matches cities in locationCorpus -> check if identifiable
                if regions is not None and regions != []:
                    # filter those cities out for which the defined region is not found in any city
                    regionids = self.locationCorpus.getWikidataIds(regions)
                    cities = list(filter(
                        lambda x: 'wikidataid' in x.getRegion().__dict__ and x.getRegion().wikidataid in regionids,
                                  cities))
                    countries = list(filter(
                        lambda x: 'wikidataid' in x.getCountry().__dict__ and x.getCountry().wikidataid in regionids,
                        cities))
                if countries is not None and countries != []:
                    # filter those cities out for which the defined country is not found in any city
                    countryids=self.locationCorpus.getWikidataIds(countries)
                    cities = list(filter(
                        lambda x: 'wikidataid' in x.getCountry().__dict__ and x.getCountry().wikidataid in countryids,
                        cities))
                if len(cities) == 1:
                    # city can be identified (Could still be incorrect)
                    final_city=cities[0]
                    if isinstance(final_city,City):
                        event[self.CITY]=final_city.getPageTitle()
                        event[self.REGION] = final_city.getRegion().getPageTitle()
                        event[self.COUNTRY] = final_city.getCountry().getPageTitle()
                        errors["complete"]="Location of event complete"
                        return event, errors
                elif len(cities) == 0:
                    # No matching city -> Two possibilities: event location information incorrect or locations missing in LocationCorpus
                    errors["city_unknown"]=f"City '{event_city}' could not be matched against a city in the LocationCorpus with the given region and country. Either location information are incorrect or location is missing in the corpus."
                    #return None, errors
                else:
                    errors["city_unclear"]=f"City '{event_city}' matches against multiple cities in the LocationCorpus. Other location information are not sufficient enough to clearly identify the city"
            else:
                # event_city is not the LocationCorpus
                isPossiblyMisplaced=True
        if event_region is not None:
            # event_city is not defined
            if regions is not None:
                if countries is not None and countries != []:
                    # filter those cities out for which the defined country is not found in any city
                    countryids=self.locationCorpus.getWikidataIds(countries)
                    regions = list(filter(
                        lambda x: 'wikidataid' in x.getCountry().__dict__ and x.getCountry().wikidataid in countryids,
                        regions))
                if len(regions)==1:
                    # region can be identified
                    final_region = regions[0]
                    if isinstance(final_region, Region):
                        event[self.REGION] = final_region.getPageTitle()
                        event[self.COUNTRY] = final_region.getCountry().getPageTitle()
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
            if countries is not None:
                if len(countries)==1:
                    final_country=countries[0]
                    event[self.COUNTRY] = final_country.getPageTitle()
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
        cities = self.locationCorpus.getCity(event_city)
        regions = self.locationCorpus.getRegion(event_region)
        countries = self.locationCorpus.getCountry(event_country)
        modified_city=False
        modified_region=False
        modified_country=False
        # check city
        if event_city is not None:
            possible_regions=self.locationCorpus.getRegion(event_city)
            possible_country=self.locationCorpus.getCountry(event_city)
            if possible_regions and possible_country is not None:
                # city could be region or country -> undecidable
                pass
            elif possible_regions is not None and regions is None:
                event[self.REGION]=event_city
                modified_region=True
                if not modified_city:
                    del event[self.CITY]
            elif possible_country is not None and countries is None:
                event[self.COUNTRY]=event_city
                modified_country=True
                if not modified_city:
                    del event[self.CITY]
        if event_region is not None:
            possible_cities=self.locationCorpus.getCity(event_region)
            possible_country=self.locationCorpus.getCountry(event_region)
            if possible_cities and possible_country is not None:
                # region could be city or country -> undecidable
                pass
            elif possible_cities is not None and cities is None:
                event[self.CITY]=event_region
                modified_city=True
                if not modified_region:
                    del event[self.REGION]
            elif possible_country is not None and countries is None:
                event[self.COUNTRY]=event_region
                modified_country=True
                if not modified_region:
                    del event[self.REGION]
        if event_country is not None:
            possible_cities=self.locationCorpus.getCity(event_country)
            possible_regions=self.locationCorpus.getRegion(event_country)
            if possible_cities and possible_regions is not None:
                # country could be city or region -> undecidable
                pass
            elif possible_cities is not None and cities is None:
                event[self.CITY]=event_country
                modified_city=True
                if not modified_country:
                    del event[self.COUNTRY]
            elif possible_regions is not None and regions is None:
                event[self.REGION] = event_country
                modified_region=True
                if not modified_country:
                    del event[self.COUNTRY]
        return modified_city or modified_region or modified_country



if __name__ == "__main__":
    fixer = LocationFixer()
    files = fixer.getAllPages("or_event_us")   # folder containing the backup files
    fixer.debug = True
    events=[]
    for filename in files[:10000]:
        content = None
        with open(filename) as file:
            content = file.read()
        wikiPage = WikiPage(content)
        event=wikiPage.extract_template("Event")
        events.append(event)
    fixer.fixEventRecords(events)