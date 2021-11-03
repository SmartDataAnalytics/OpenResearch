'''
Created on 2021-09-27

@author: th
'''
import re

from corpus.datasources.wikicfp import WikiCfp
from corpus.lookup import CorpusLookup
from corpus.quality.rating import RatingType

from ormigrate.fixer import ORFixer, Entity
from ormigrate.smw.rating import EntityRating


class WikiCfpIdSeriesFixer(ORFixer):
    """
    Fixes the WikiCfp id of an event series
    see https://github.com/SmartDataAnalytics/OpenResearch/issues/256
    """

    purpose = "fixer for getting WikiCFP id from the events of the event series"
    issue = "https://github.com/SmartDataAnalytics/OpenResearch/issues/256"

    worksOn = [Entity.EVENT_SERIES]

    wikiCfpIdRegex=r"^[1-9]\d*$"  # https://www.wikidata.org/wiki/Property:P5127
    wikiCfpSeriesUriRegex="^https?:\/\/wikicfp\.com\/cfp\/program\?id=(?P<id>[1-9]\d*)" # https://www.wikidata.org/wiki/Property:P5127 slighty modified with a named group
    WIKI_CFP_SERIES="wikiCfpSeries"   # normalized property name
    WIKI_CFP_ID="wikicfpId"

    def __init__(self,pageFixerManager):
        """
        Constructor
        Args:
            pageFixerManager: manager who manages this fixer
        """
        super(WikiCfpIdSeriesFixer, self).__init__(pageFixerManager)
        self.wikiCfpDataSource=self.getWikiCFPDataSource()
        self.wikiCfpEventLookup, _dup = self.wikiCfpDataSource.eventManager.getLookup("eventId")
        self.seriesLookup=None

    def getWikiCFPDataSource(self):
        """Returns the WikiCfpDataSource of the ConferenceCorpus"""
        cfpDataSource = WikiCfp()
        cfpDataSource.load()
        return cfpDataSource


    def getEventsOfSeries(self, seriesAcronym):
        """Returns the events that are in the series with the given acronym"""
        eventManager=self.pageFixerManager.orDataSource.eventManager
        eventSeriesManager=self.pageFixerManager.orDataSource.eventSeriesManager
        if self.seriesLookup is None:
            # this reinitializing of the lookup tables need to be done to integrate the fixes of previous fixers
            # into the lookup lists
            eventManager.linkSeriesAndEvent(eventSeriesManager, "inEventSeries")
            self.seriesLookup=eventManager.seriesLookup

        events=self.seriesLookup.get(seriesAcronym)
        return events

    def getWikiCFPSeriesIdOfEvent(self, eventId:str):
        """
        returns the wikiCFPSeries id of the given wikiCFP ID
        Args:
            eventId: wikiCFP id of an event for which the series id should be returend

        Returns:
            str wikiCFP series id
        """
        if eventId in self.wikiCfpEventLookup:
            event=self.wikiCfpEventLookup.get(eventId)
            seriesId=getattr(event, "seriesId")
            if seriesId:
                return seriesId

    def fix(self,rating:EntityRating):
        """
        fixes the given Enity by trying to set the wikiCFP id
        Args:
            rating: EntityRating including the entity that should be fixed

        Returns:
            Nothing
        """
        record = rating.getRecord()
        wikiCfpId = record.get(self.WIKI_CFP_SERIES)
        if wikiCfpId:
            # id is present
            if bool(re.search(self.wikiCfpSeriesUriRegex, wikiCfpId)):
                # wikicfp id is in the uri
                match=re.match(self.wikiCfpSeriesUriRegex, wikiCfpId)
                record[self.WIKI_CFP_SERIES]=match.group("id")
        else:
            # try to fin the wikiCFP id of the series
            acronym=record.get("acronym")
            if acronym is None:
                acronym=rating.pageTitle
            events=self.getEventsOfSeries(acronym)
            if events is not None:
                wikiCfpIdsOfEvents={getattr(event, self.WIKI_CFP_ID) for event in events if hasattr(event, self.WIKI_CFP_ID)}
                possibleWikiCFPSeriesIds={self.getWikiCFPSeriesIdOfEvent(eventId) for eventId in wikiCfpIdsOfEvents}
                reg = re.compile(self.wikiCfpIdRegex)
                possibleWikiCFPSeriesIds=list(filter(reg.search, filter(None,possibleWikiCFPSeriesIds)))
                if len(possibleWikiCFPSeriesIds) == 1:
                    # wikiCFP series id is distinct
                    record[self.WIKI_CFP_SERIES]=possibleWikiCFPSeriesIds.pop()

    def rate(self,rating:EntityRating):
        """
        rates the given entity in regard of the wikiCFP id
        Args:
            rating: EntityRating including the entity that should be rated

        Returns:
            Nothing
        """
        record=rating.getRecord()
        wikiCfpId = record.get(self.WIKI_CFP_SERIES)
        if wikiCfpId:
            if bool(re.search(self.wikiCfpIdRegex, wikiCfpId)):
                # property value has the correct format
                rating.set(1, RatingType.ok, "wikiCFP ID is present and in correct format")
            elif bool(re.search(self.wikiCfpSeriesUriRegex, wikiCfpId)):
                rating.set(3,RatingType.ok,"wikicfp ID has wrong format (ID inside of URI)")
            else:
                # property is present but has an invalid format
                rating.set(5, RatingType.invalid, f"The wikiCFP ID '{wikiCfpId}' does not have the correct format")
        else:
            # property value is missing
            rating.set(7, RatingType.missing, "wikiCFP ID is missing")
