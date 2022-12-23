"""
Created on 2021-04-06

@author: wf
"""
import sys
import inspect
import typing
from pathlib import Path

from corpus.datasources.openresearch import OR, OREvent, OREventManager, OREventSeries, OREventSeriesManager
from corpus.utils.download import Profiler
from lodstorage.entity import EntityManager
from lodstorage.lod import LOD
from lodstorage.sql import SQLDB
from tabulate import tabulate
from wikifile.wikiFileManager import WikiFileManager
from wikifile.cmdline import CmdLineAble
from wikifile.wikiRender import WikiFile
from ormigrate.smw.rating import RatingType, PageRating, EntityRating
from collections import Counter
from ormigrate.smw.templates import RatingTemplatePage, RatedEventTemplatePage, RatedEventSeriesTemplatePage


class PageFixerManager(object):
    """
    manage a list of PageFixers
    """
    
    def __init__(
            self,
            pageFixerClassList: list,
            wikiFileManager: WikiFileManager,
            ccID: str = "orclone-backup",
            pageTitles: str = None,
            debug: bool = False,
            forceUpdate: bool = False
    ):
        """
        construct me

        Args:
            pageFixerClassList(list): a list of pageFixers
            ccID(str): ConferenceCorpus source lookup id
            forceUpdate(bool): If true forceUpdate the ConferenceCorpus datasources
        """
        self.pageFixerClassList = pageFixerClassList
        self.pageFixers = {}
        self.debug = debug
        self.wikiFileManager = wikiFileManager
        self.orDataSource = self.loadOR(wikiFileManager=wikiFileManager, ccId=ccID)
        for pageFixerClass in pageFixerClassList:
            pageFixer = pageFixerClass(self)
            pageFixerClassName = pageFixerClass.__name__
            self.pageFixers[pageFixerClassName] = pageFixer

        # load wikiFiles for each entity
        self.wikifile_lookup = self.load_wiki_files()
        self.setupEntityRatings(pageTitles)

    def load_wiki_files(self) -> typing.Dict[str, WikiFile]:
        """
        load the WikiFiles of events and event series

        Returns:
            Lookup map from pageTitle to WikiFile
        """
        wikifile_lookup = dict()
        for entity_manager in self.orDataSource.eventManager, self.orDataSource.eventSeriesManager:
            records = entity_manager.getList()
            for record in records:
                page_title = getattr(record, "pageTitle")
                wikifile = self.wikiFileManager.getWikiFile(page_title)
                wikifile_lookup[page_title] = wikifile
        return wikifile_lookup

    def loadOR(self, wikiFileManager: WikiFileManager, ccId:str):
        """
        loads the OR to memory

        Args:
            wikiFileManager:
            ccId: if None try to load from

        Returns:

        """
        if ccId is None:
            # load from file to memory
            datasource = OR(self.wikiFileManager.sourceWikiId, via="backup")
            # self.patchEventSource(datasource, wikiFileManager=wikiFileManager)
            msg = f"loading {datasource.sourceConfig.title}"
            profiler = Profiler(msg=msg, profile=self.debug)
            datasource.eventSeriesManager.configure()
            event_manager = datasource.eventManager
            if isinstance(event_manager, OREventManager):
                event_manager.configure()
                event_manager.setListFromLoD(event_manager.getLoDfromWikiFileManager())
            series_manager = datasource.eventSeriesManager
            if isinstance(series_manager, OREventSeriesManager):
                series_manager.setListFromLoD(series_manager.getLoDfromWikiFileManager())
                event_manager.linkSeriesAndEvent(series_manager, "inEventSeries")
            profiler.time()
        else:
            # load from ConferenceCorpus
            idParts = ccId.split("-")
            wikiId = idParts[0]
            via = "api"
            if len(idParts) == 2:
                via = idParts[1]
            datasource = OR(wikiId, via=via)
            #self.patchEventSource(datasource, wikiFileManager=wikiFileManager)
            datasource.load()
        return datasource

    @property
    def ratings(self):
        """Returns the EntityRatings of all fixers and entities"""
        res=[]
        if hasattr(self, 'entityRatings'):
            for pageFixerRatings in self.entityRatings.values():
                for entityRatings in pageFixerRatings.values():
                    res.extend(entityRatings)
        return res

    @staticmethod
    def runCmdLine(pageFixerClassList: list = None, argv: list = None):
        """
        Args:
            pageFixerClassList(list): a list of page fixers to apply
            argv(list): the command line arguments to use
        Returns:
            a pageFixerManager that has completed the work as specified
            in the arguments
        """
        if argv is None:
            argv = ["-s", "orclone", "--stats"]
        pageFixerManager = PageFixerManager.fromCommandLine(pageFixerClassList, argv)
        if pageFixerManager:
            pageFixerManager.workOnArgs()
        return pageFixerManager
     
    @staticmethod
    def fromCommandLine(pageFixerClassList: list = None, argv: list = None):
        """
        construct a pageFixerList from the command line with the given Arguments
        Args:
            pageFixerClassList: a list of page fixers to apply
            argv: the command line arguments to use

        Returns:

        """
        cmdLine = CmdLineAble()
        cmdLine.getParser()
        cmdLine.parser.add_argument(
                "--stats",
                action="store_true",
                help="calculate and show rating statistics")
        cmdLine.parser.add_argument(
                "--listRatings",
                action="store_true",
                help="calculate and show Ratings as a list of links")
        cmdLine.parser.add_argument(
                "--verbose",
                action="store_true",
                help="shows verbose output")
        cmdLine.parser.add_argument(
                "--fix",
                action="store_true",
                help="Fix the Event pages")
        cmdLine.parser.add_argument(
                "--force",
                default=False,
                action="store_true",
                help="Overwrite existing files")
        cmdLine.parser.add_argument(
                '--targetWikiTextPath',
                dest="targetWikiTextPath",
                help="Path to store/update the wiki entries")
        cmdLine.parser.add_argument(
                "--fixers",
                nargs='+',
                help="Name of the fixers to apply")
        cmdLine.parser.add_argument(
                "--listFixers",
                action="store_true",
                help="List all avaliable fixers")
        cmdLine.parser.add_argument(
                "--ccId",
                help="Id of the ConferenceCorpus data source to use")
        cmdLine.parser.add_argument(
                "--tableFormat",
                help="Format the resulting table should have. E.g. mediawiki, github, table")
        cmdLine.parser.add_argument(
                "--addRatingPage",
                action="store_true",
                help="adds a rating subpage for each entity containing the ratings of the entity")
        cmdLine.parser.add_argument(
                "--genTechPages",
                default=False,
                action="store_true",
                help="Generate the technical entity pages such as Help: Category: List of etc. and their properties")
        if argv is None:
            argv = sys.argv[1:]
        args = cmdLine.parser.parse_args(argv)
        cmdLine.initLogging(args)
        pageFixers = PageFixerManager.getAllFixers()
        if args.listFixers:
            print("Available fixers:")
            res = []
            for pageFixer in pageFixers:
                pfDesc = {"name": pageFixer.__name__}
                for key in "purpose", "issue":
                    if hasattr(pageFixer, key):
                        pfDesc[key] = getattr(pageFixer,key)
                res.append(pfDesc)
            print(tabulate(tabular_data=res, headers="keys"))
            return
        if pageFixerClassList is None:
            pageFixerClassList = []
        if args.fixers:
            pageFixersByName = {pf.__name__: pf for pf in pageFixers}
            for fixer in args.fixers:
                if fixer in pageFixersByName:
                    pageFixerClassList.append(pageFixersByName.get(fixer))
        if args.verbose:
            print(f"Starting pagefixers for {args.source}")
        wikiTextPath = args.backupPath
        if not wikiTextPath and args.ccId:
            wikiTextPath = f"{Path.home()}/.or/wikibackup/{args.ccId.replace('-backup', '')}"
        wikiFileManager = WikiFileManager(
                sourceWikiId=args.source,
                wikiTextPath=wikiTextPath,
                targetWikiTextPath=args.targetWikiTextPath,
                login=False,
                debug=args.debug
        )
        pageFixerManager = PageFixerManager(
                pageFixerClassList,
                wikiFileManager=wikiFileManager,
                ccID=args.ccId,
                pageTitles=args.pages,
                debug=args.debug,
                forceUpdate=args.force
        )
        for pageFixer in pageFixerManager.pageFixers.values():
            pageFixer.templateName = args.template
        pageFixerManager.args = args
        return pageFixerManager
        
    def workOnArgs(self):
        """
        work as specified by my arguments
        """
        if self.args.debug:
            print(f"found {len(self.wikiFilesToWorkon)} pages to work on")
        if self.args.stats or self.args.listRatings or self.args.addRatingPage:
            self.getRatings(debug=self.args.debug)
        if self.args.stats:
            self.showRatingStats()
        if self.args.listRatings:
            self.showRatingList(self.args.tableFormat)
        if self.args.addRatingPage:
            # add rating to rating subpage before fixers are applied
            self.addRatingSubPages()
        if self.args.fix:
            self.fix(self.args.force)
            if self.args.addRatingPage or self.args.stats:
                # add rating to rating subpage after fixers are applied
                self.getRatings(debug=self.args.debug, onlyIfHasFixer=True)   # rate entities again (only if they were fixed)
                if self.args.stats:
                    self.showRatingStats()
                if self.args.addRatingPage:
                    self.addRatingSubPages(afterFixing=True)
        if self.args.genTechPages:
            # generate rating topic and property pages
            self.generateTechnicalEntityPages(self.wikiFileManager, overwrite=self.args.force)

    def setupEntityRatings(self, pageTitles: list = None):
        """
        Generates for each fixer their EntityRating objects
        """
        entityRatings = dict()
        from ormigrate.fixer import Entity
        for fixerName, fixer in self.pageFixers.items():
            eventRatings = []
            eventSeriesRatings = []
            if Entity.EVENT in fixer.worksOn:
                eventRatings = []
                for entity in self.orDataSource.eventManager.getList():
                    entity_rating = EntityRating(entity=entity, fixer=fixer)
                    entity_rating.wikiFile = self.wikifile_lookup.get(entity_rating.pageTitle)
                    eventRatings.append(entity_rating)
            if Entity.EVENT_SERIES in fixer.worksOn:
                eventSeriesRatings = []
                for entity in self.orDataSource.eventSeriesManager.getList():
                    entity_rating = EntityRating(entity=entity, fixer=fixer)
                    entity_rating.wikiFile = self.wikifile_lookup.get(entity_rating.pageTitle)
                    eventSeriesRatings.append(entity_rating)
            if pageTitles:
                eventRatings = [e for e in eventRatings if e.pageTitle in pageTitles]
                eventSeriesRatings = [e for e in eventSeriesRatings if e.pageTitle in pageTitles]
            entityRatings[fixerName] = {
                Entity.EVENT: eventRatings,
                Entity.EVENT_SERIES: eventSeriesRatings
            }
        self.entityRatings = entityRatings

    def getEventRatingsForFixer(self, fixer: type):
        """Returns the EventRatings the given fixer can work on"""
        entityRatings = self.entityRatings.get(fixer.__class__.__name__)
        res = []
        if hasattr(fixer, "worksOn"):
            for entityType in fixer.worksOn:
                res.extend(entityRatings.get(entityType))
        return res

    def fix(self, overwrite: bool = False):
        """
        Fix the wikiFiles by calling the fix functions of the pageFixers
        Args:
            overwrite(bool): If True existing files might be overwritten
        """
        for pageFixer in self.pageFixers.values():
            if not self.hasFixer(pageFixer):
                continue
            entityRatings = self.getEventRatingsForFixer(pageFixer)
            total = len(entityRatings)
            count = 0
            for entityRating in entityRatings:
                pageFixer.fix(entityRating)
                count += 1
                print(f"{pageFixer.__class__.__name__}: {count}/{total} fixed", end='\r'if count != total else "\n")
                self.save_entity_rating_to_wikimarkup(entityRating, overwrite=overwrite)
        # all fixes are applied → save back to wikiText file
        print("saving the applied fixes to the wikiMarkup files")
        entities = {entityRating.entity for entityRating in self.ratings}
        total = len(entities)
        count = 0
        for entity in entities:
            self.save_entity_rating_to_wikimarkup(entity, overwrite=overwrite)
            count += 1
            print(f"{count}/{total} Entities saved to wikiMarkup file", end='\r'if count != total else "\n")

    def save_entity_rating_to_wikimarkup(
            self,
            entity: typing.Union[EntityRating, OREvent, OREventSeries],
            overwrite: bool = False
    ):
        """
        Save the properties of the given entityRating to wikimarkup by updating the wikitext
        Args:
            entity: entity to save
            overwrite: If True existing files might be overwritten
        """
        wikifile = None
        if isinstance(entity, EntityRating) and isinstance(entity.wikiFile, WikiFile):
            wikifile = entity.wikiFile
        else:
            wikifile = self.wikifile_lookup.get(getattr(entity, "pageTitle"))
        prop_map = self.get_entity_property_lookup(entity)
        entity_record = entity.getRecord() if isinstance(entity, EntityRating) else entity.__dict__
        record = self.map_dict_keys(entity_record, prop_map)
        wikifile.updateTemplate(entity.templateName, args=record, overwrite=overwrite)
        wikifile.save_to_file(overwrite=overwrite)

    @staticmethod
    def map_dict_keys(record: dict, key_map: typing.Dict[str, str]):
        """
        Map the keys of the given record based on the given map to new key names
        Args:
            record: record to map
            key_map: key mapping

        Returns:
            dict with new keys
        """
        res = dict()
        for key, new_key in key_map.items():
            if key in record:
                res[new_key] = record[key]
        return res

    def get_entity_property_lookup(
            self,
            entity: typing.Union[EntityRating, OREvent, OREventSeries]
    ) -> typing.Dict[str, str]:
        """
        Get the property lookup for the given entity
        Args:
            entity:

        Returns:
            property mapping from entity property to target property
        """
        prop_map = dict()
        if isinstance(entity, EntityRating):
            entity = entity.entity
        if isinstance(entity, OREvent):
            prop_map = {item: key for key, item in OREvent.getTemplateParamLookup().items()}
        elif isinstance(entity, OREventSeries):
            prop_map = {item: key for key, item in OREventSeries.getTemplateParamLookup().items()}
        return prop_map

    def getRatings(self, debug: bool, debugLimit: int = 10, onlyIfHasFixer:bool=False):
        """
        get the ratings for my pageFixers

        Args:
            debug(bool): should debug information be printed
            debugLimit(int): maximum number of debug message to be printed
            onlyIfHasFixer(bool): If True the entity is only rated if the Fixer provides a fixing function
        """
        total = len(self.ratings)
        count = 0
        for rating in self.ratings:
            if isinstance(rating, EntityRating):
                if onlyIfHasFixer and not self.hasFixer(rating.fixer):
                    # don't rate fixer has no fix function and onlyIfHasFixer is True
                    continue
            rating.rate()
            count += 1
            print(f"{count}/{total} rated", end='\r' if count != total else "\n")
                
    def getRatingCounters(self):
        """
        get the ratingCounter
        """
        counters = {}
        for attr in ["reason", "pain"]:
            counters[attr] = {}
            for fixer in self.pageFixers:
                counter = Counter()
                ratings = self.getEventRatingsForFixer(self.pageFixers.get(fixer))
                for rating in ratings:
                    if hasattr(rating, attr):   # If not rated the attr is not set and thus not included in the counters
                        counter[getattr(rating, attr)] += 1
                counters[attr][fixer] = counter
        return counters
    
    def showRatingList(self, tablefmt: str = 'table'):
        """
        show a list of ratings
        Args:
            tablefmt: format of the table
        """
        if tablefmt is None:
            tablefmt = "table"
        ratings = [rating.__dict__ for rating in self.ratings if rating.pain>=0]
        for rating in ratings:
            entity = rating.get("entity")
            if hasattr(entity, "pageTitle"):
                rating["pageTitle"] = getattr(entity, "pageTitle")
            if hasattr(entity, "url"):
                rating["url"] = getattr(entity, "url")
        mandatoryFields = [*EntityRating.getSamples()[0].keys(), "url"]
        displayRatings = LOD.filterFields(ratings, fields=mandatoryFields, reverse=True)
        print(tabulate(displayRatings, headers="keys", tablefmt=tablefmt))
        
    def showRatingStats(self):
        """
        show the rating statistics
        """
        tableFormat = getattr(self.args, "tableFormat")
        if tableFormat is None:
            tableFormat = "table"
        counters = self.getRatingCounters()
        fixerCounter = counters["reason"]
        print("Rating:")
        reasonTable = {}
        for fixer, counter in fixerCounter.items():
            total = sum(counter.values())
            for ratingType in counter:
                ratingTypeCount = counter[ratingType]
                fixerReason = f"{ratingTypeCount:5d} ({ratingTypeCount/total*100:5.1f}%)"
                if ratingType in reasonTable:
                    reasonTable[ratingType][fixer] = fixerReason
                else:
                    reasonTable[ratingType] = {"Reason":ratingType.value, fixer:fixerReason}
        print(tabulate(reasonTable.values(), headers="keys", tablefmt=tableFormat))
        fixerCounter = counters["pain"]
        painTable = {}
        for fixer, counter in fixerCounter.items():
            total = sum(counter.values())
            for pain in sorted(counter):
                painCount = counter[pain]
                fixerPain = f"{painCount:5d} ({painCount/total*100:5.1f}%)"
                if pain in painTable:
                    painTable[pain][fixer] = fixerPain
                else:
                    painTable[pain] = {"Pain": f"{pain:2d}", fixer: fixerPain}
        print(tabulate(painTable.values(), headers="keys", tablefmt=tableFormat))

    def showAllRatings(self):
        for i,pageTitle in enumerate(self.ratings):
            print(f"{i+1}:{pageTitle}->{self.ratings[pageTitle]}")

    @staticmethod
    def getAllFixers() -> typing.List[type]:
        """
        Get all fixer classes

        Returns:
            list of all fixer classes
        """
        import ormigrate
        import pkgutil
        from ormigrate.fixer import ORFixer
        pagefixers = []
        for importer, modname, ispkg in pkgutil.iter_modules(ormigrate.__path__):
            module = __import__(f"ormigrate.{modname}")
            clsmembers = inspect.getmembers(getattr(module, modname), inspect.isclass)
            pageFixer = []
            for name, clazz in clsmembers:
                if issubclass(clazz, (ORFixer, PageFixer)) and hasattr(clazz, 'purpose'):
                    pageFixer.append(clazz)
            pagefixers.extend(pageFixer)
        pagefixers = list(set(pagefixers))
        return pagefixers

    def addRatingSubPages(self, overwrite: bool = True, afterFixing: bool = False):
        """
        Generate the Rating subpages
        Args:
            overwrite:
            afterFixing:
        """
        wikiFileManager = WikiFileManager(
                self.wikiFileManager.sourceWikiId,
                self.wikiFileManager.targetPath,
                login=False
        )
        # add rating entities
        postfix = "After" if afterFixing else ""
        total = len(self.ratings)
        count = 0
        for pageFixer in self.pageFixers.values():
            entityRatings = self.getEventRatingsForFixer(pageFixer)
            if afterFixing and not self.hasFixer(pageFixer):
                count += len(entityRatings)
                print(f"{count}/{total} Ratings added to the rating page", end='\r' if count != total else "\n")
                continue
            for ratingEntity in entityRatings:
                if ratingEntity.pain != -1:
                    wikiFile = wikiFileManager.getWikiFile(f"{ratingEntity.pageTitle}/rating", checkWiki=False)
                    if not wikiFile.wikiText:
                        # rating subpage does not exist → add Headline with link to original entity
                        wikiFile.wikiText = f"== Ratings for [[{ ratingEntity.pageTitle }]]=="
                    rating = {
                        "fixer": ratingEntity.fixer.__class__.__name__,
                        f"pain{postfix}": f"{ratingEntity.pain}",
                        f"reason{postfix}": str(ratingEntity.reason.value),
                        f"hint{postfix}": str(ratingEntity.hint),
                        "storemode": "subobject",
                        "viewmode": "ratingOnly" if not self.hasFixer(pageFixer) else "ratingComparison"
                    }
                    wikiFile.updateTemplate(
                            template_name="Rating",
                            args=rating,
                            match={"fixer": ratingEntity.fixer.__class__.__name__},
                            prettify=True
                    )
                    wikiFile.save_to_file(overwrite=overwrite)
                    count += 1
                    print(f"{count}/{total} Ratings added to the rating page", end='\r' if count != total else "\n")

    def generateTechnicalEntityPages(self, wikiFileManager: WikiFileManager, overwrite: bool = False):
        """
        Generates the technical pages for the entityRating, Event and Event series
        Args:
            wikiFileManager: WikiFileManager (specifies the target location of the generated files)
            overwrite: If True existing files will be overwritten

        Returns:
            Nothing
        """
        from ormigrate.EventLocationHandler import EventLocationHandler
        # pages for fixer topic
        EventLocationHandler.generateTechnicalPages(
                "fixer",
                wikiFileManager,
                overwrite=overwrite)
        # pages for rating topic
        EventLocationHandler.generateTechnicalPages(
                "rating",
                wikiFileManager,
                overwrite=overwrite,
                template=RatingTemplatePage)
        # pages for event topic
        EventLocationHandler.generateTechnicalPages(
                "event",
                wikiFileManager,
                overwrite=overwrite,
                templateParamMapping=self.getPropertyToTemplateParamMap(self.orDataSource.eventManager),
                template=RatedEventTemplatePage)
        # pages for event series topic
        EventLocationHandler.generateTechnicalPages(
                "eventSeries",
                wikiFileManager,
                overwrite=overwrite,
                templateParamMapping=self.getPropertyToTemplateParamMap(self.orDataSource.eventSeriesManager),
                template=RatedEventSeriesTemplatePage)

    def generateFixerPages(self, overwrite: bool = False):
        """
        Generates the pages for all fixers
        Args:
            overwrite:
        """
        from ormigrate.EventLocationHandler import EventLocationHandler
        # pages for fixer topic
        EventLocationHandler.generateTechnicalPages(
                "fixer",
                self.wikiFileManager,
                overwrite=overwrite)
        for name, pageFixer in self.pageFixers.items():
            wikiFile = self.wikiFileManager.getWikiFile(name, checkWiki=False)
            fixer = {
                "name": name,
                "issue": str(pageFixer.issue).replace("https://github.com/SmartDataAnalytics/OpenResearch/issues/",""),
                "purpose": pageFixer.purpose
            }
            wikiFile.updateTemplate("Fixer", fixer, match={"name": name}, prettify=True)
            wikiFile.save_to_file(overwrite=overwrite)

    def getPropertyToTemplateParamMap(self, manager: EntityManager):
        """
        Returns the mapping from property names to template parameter names for the given EntityManager
        Args:
            manager: EntityManager for which the mapping should be returned

        Returns:
            Dict
        """
        if callable(getattr(manager.clazz, "getTemplateParamLookup", None)):
            templateParamMapping = {v: k for k, v in manager.clazz.getTemplateParamLookup().items()}
            return templateParamMapping
        return {}

    @staticmethod
    def hasFixer(pageFixer):
        """
        Checks if the given fixer implements the fix function
        Args:
            pageFixer:
        """
        entityFixerClasses = [fixer for fixer in pageFixer.__class__.mro() if fixer.__name__ == "EntityFixer"]
        if entityFixerClasses:
            entityFixerClass = entityFixerClasses[0]
            if callable(getattr(pageFixer.__class__, "fix", None)):
                return getattr(entityFixerClass, "fix") != getattr(pageFixer.__class__, "fix")
        return False
    
    
class PageFixer(object):
    """
    general fixer for wiki pages
    """

    def __init__(self, pageFixerManager: PageFixerManager, debug: bool = False):
        """
        Constructor
        Args:
            pageFixerManager:
            debug:
        """
        self.debug=debug
        self.pageFixerManager=pageFixerManager
        self.wikiFileManager=pageFixerManager.wikiFileManager

    def fixEventRecord(self, **kwargs):
        """ abstract base function to be overwritten by fixing class"""
        return

    def getRatingFromWikiFile(self, wikiFile: WikiFile)->PageRating:
        """
        Args:
            wikiFile(WikiFile): the wikiFile to work on

        Return:
            Rating: The rating for this WikiFile

        """
        # prepare rating
        _wikiText, eventRecord, rating = self.prepareWikiFileRating(wikiFile, self.templateName)
        # rating=Rating(6,RatingType.invalid,f"{self.__class__.__name__} has no rating implementation for {wikiFile.getPageTitle()}")
        arating = self.getRating(eventRecord)
        rating.set(arating.pain, arating.reason, arating.hint)
        return rating

    def prepareWikiFileRating(self, wikifile: WikiFile, template_name: str = None):
        """
        prepare the rating of an entity record directly from the wikiFile
        """
        if template_name is None:
            template_name = getattr(self, "templateName", None)
        # get the markup
        wiki_markup = str(wikifile)
        # retrieve the name/value list
        template_records = wikifile.extractTemplate(template_name)
        # retrieve the page Title
        page_title = wikifile.getPageTitle()
        if len(template_records) > 0:
            template_record = template_records[0]
            # convert the content according to the property lookup
            property_lookup = dict()
            if template_name == OREvent.templateName:
                property_lookup = OREvent.getTemplateParamLookup()
            elif template_name == OREventSeries.templateName:
                property_lookup = OREventSeries.getTemplateParamLookup()
            # create a proper entity record
            entity_record = PageFixerManager.map_dict_keys(template_record, property_lookup)
        else:
            entity_record = dict()
        # create a default bad rating
        rating = PageRating(page_title, template_name, 7, RatingType.missing, "rating error")
        return wiki_markup, entity_record, rating

    def getConferenceCorpusSqlDb(self) -> SQLDB:
        """
        Get ConferenceCorpus database as SQL connector
        Returns:
            SQLDB: ConferenceCorpus db
        """
        cache_file = self.pageFixerManager.orDataSource.eventManager.getCacheFile()
        db = self.pageFixerManager.orDataSource.eventManager.getSQLDB(cache_file)
        return db

    
class EntityFixer(PageFixer):
    """
    fixer for entities
    """
    
    def __init__(self, pageFixerManager: PageFixerManager, debug: bool = False):
        """
        constructor
        Args:
            pageFixerManager:
            debug:
        """
        super(EntityFixer, self).__init__(pageFixerManager, debug)
        self.propertyLookups = {}
        
    def rate(self, rating: EntityRating):
        """
        Hollywood style callback with a prepared rating to be filled with the
        actual rating of this fixer. So the fixer needs to modify this rating accordingly.

        Args:
            rating(EntityRating): the rating for a single entity
        """
        raise Exception("rate not implemented")
        pass
    
    def fix(self, rating: EntityRating):
        """
        Hollywood style callback with a prepared rating that has already been rated.
        The fixer will provide a fixing proposal by providing a modified version of the
        entity and potentially the corresponding WikiText.

        Args:
            rating(EntityRating): the rating for a single entity
        """
        raise Exception("fix not implemented")


if __name__ == '__main__':
    PageFixerManager.runCmdLine()