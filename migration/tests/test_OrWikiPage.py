import json
import uuid
from corpus.datasources.openresearch import OREvent, OREventSeries
from ormigrate.smw.orwikipage import OrWikiPage, main
from tests.basetest import ORMigrationTest


class TestOrWikiPage(ORMigrationTest):
    """
    tests OrWikiPage
    """

    def setUp(self, debug:bool=False, profile:bool=True):
        super().setUp(debug, profile)
        self.testWikiId = "test"
        if not self.inCI():
            self.orWikiPage = OrWikiPage(wikiId=self.testWikiId)

    def test_updateEvent(self):
        """
        tests updating an event
        """
        if self.inCI():
            return
        pageTitle = str(uuid.uuid1())
        eventRecord = OREvent.getSamples()[0]
        self.orWikiPage.updateEvent(pageTitle=pageTitle, props=eventRecord, updateMsg="test_updateEvent", denormalizeProperties=True)
        wikiRecord = self.orWikiPage.getWikiSonFromPage(pageTitle, OREvent.templateName)
        expectedRecord = self.orWikiPage.normalizeProperties(eventRecord, OREvent, reverse=True)
        for k, v in expectedRecord.items():
            self.assertIn(k, wikiRecord)
            self.assertEqual(wikiRecord[k], str(v))

    def test_updateEventSeries(self):
        """
        tests updating an event series
        """
        if self.inCI():
            return
        pageTitle = str(uuid.uuid1())
        eventRecord = OREventSeries.getSamples()[0]
        self.orWikiPage.updateEventSeries(pageTitle=pageTitle, props=eventRecord, updateMsg="test_updateEventSeries", denormalizeProperties=True)
        wikiRecord = self.orWikiPage.getWikiSonFromPage(pageTitle, OREventSeries.templateName)
        expectedRecord = self.orWikiPage.normalizeProperties(eventRecord, OREventSeries, reverse=True)
        for k, v in expectedRecord.items():
            self.assertIn(k, wikiRecord)
            self.assertEqual(wikiRecord[k], str(v))

    def test_noramlizeProperties(self):
        """
        tests normalizeProperties() conversion from template properties to normalized properties and vice versa
        """
        propMap = OREvent.getTemplateParamLookup()
        template_dict = {k: "test value" for k in propMap.keys()}
        normalized_dict = {v: "test value" for v in propMap.values()}
        self.assertDictEqual(normalized_dict, OrWikiPage.normalizeProperties(template_dict, OREvent))
        self.assertDictEqual(template_dict, OrWikiPage.normalizeProperties(normalized_dict, OREvent, reverse=True))

    def test_normalizeProperties_propertyExclution(self):
        """
        tests normalizeProperties() excluding of properties that are not in the getTemplateParamLookup of the entity
        """
        record = {"Property that is not in the getTemplateParamLookup": "Should be excluded if force=False"}
        self.assertWarns(Warning, OrWikiPage.normalizeProperties, record, OREvent, force=False)
        self.assertEqual(dict(), OrWikiPage.normalizeProperties(record, OREvent, force=False))
        self.assertEqual(record,OrWikiPage.normalizeProperties(record, OREvent, force=True))

    def test_getPageUrl(self):
        """
        tests generating the page url
        """
        if self.inCI():
            return
        wikiPage = OrWikiPage("orclone")
        url = wikiPage.getPageUrl("AAAI")
        expectedUrl = "https://confident.dbis.rwth-aachen.de/or/index.php?title=AAAI"
        self.assertEqual(expectedUrl, url)

    def test_cmdlineInterfaceOfOrWikiPage_query(self):
        """
        tests the cmdline interface of OrWikipage specifically the querying of an entity record
        """
        if self.inCI():
            return
        record = main(['', '--wikiId', 'orfixed', '-et', 'Event', '-p', 'AAAI 2020', '--raw'])
        self.assertEqual('1227124856', record['gndId'], f"gndId not found in {record}")

    def test_cmdlineInterfaceOfOrWikiPage_update(self):
        """
        tests the cmdline interface of OrWikipage specifically the updating of an entity record
        """
        if self.inCI():
            return
        record = {
            "acronym": "Test Event",
            "year": 2000
        }
        recordStr = json.dumps(record)
        pageTitle = str(uuid.uuid1())
        # create page and WikiSON object
        main(['','--wikiId', self.testWikiId, '-et', 'Event', '-p', pageTitle, '-v', recordStr])
        # query page and check existence
        actualRecord = main(['', '--wikiId', self.testWikiId, '-et', 'Event', '-p', pageTitle])
        self.assertEqual(len(actualRecord), len(record))
        # update some properties of the record
        updateRecord = {"year":2022}
        main(['', '--wikiId', self.testWikiId, '-et', 'Event', '-p', pageTitle, '-v', json.dumps(updateRecord)])
        # check if change was applied
        actualRecord = main(['', '--wikiId', self.testWikiId, '-et', 'Event', '-p', pageTitle])
        self.assertEqual(actualRecord['year'], str(updateRecord['year']))

