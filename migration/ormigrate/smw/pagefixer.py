'''
Created on 2021-04-06

@author: wf
'''
import sys
import traceback
import inspect
from functools import partial
from os import path
from corpus.datasources.openresearch import OREventManager
from corpus.lookup import CorpusLookup
from lodstorage.lod import LOD
from tabulate import tabulate
from wikifile.wikiFileManager import WikiFileManager
from wikifile.cmdline import CmdLineAble
from wikifile.wikiRender import WikiFile
from corpus.smw.topic import SMWEntity, SMWEntityList
from ormigrate.smw.rating import RatingType,PageRating, PageRatingList, EntityRating
from collections import Counter


class PageFixerManager(object):
    '''
    manage a list of PageFixers
    '''
    
    def __init__(self,pageFixerClassList,wikiFileManager:WikiFileManager, ccID:str="orclone-backup",debug=False):
        ''' 
        construct me 
        
        Args:
            pageFixerClassList(list): a list of pageFixers
            ccID(str): ConferenceCorpus source lookup id
        '''
        self.pageFixerClassList=pageFixerClassList
        self.pageFixers={}
        self.debug=debug
        self.wikiFileManager=wikiFileManager
        for pageFixerClass in pageFixerClassList:
            pageFixer=pageFixerClass(self)
            pageFixerClassName=pageFixerClass.__name__
            self.pageFixers[pageFixerClassName]=pageFixer

        patchEventSource=partial(self.patchEventSource, wikiFileManager=wikiFileManager)
        lookup = CorpusLookup(lookupIds=[ccID], configure=patchEventSource, debug=debug)
        lookup.load(forceUpdate=True)   # forceUpdate to init the managers from the markup files
        self.orDataSource = lookup.getDataSource("orclone-backup")
        # load wikiFiles for each entity
        for entityManager in self.orDataSource.eventManager, self.orDataSource.eventSeriesManager:
            if hasattr(entityManager, 'smwHandler'):
                entityManager.smwHandler.interlinkEnititesWithWikiMarkupFile()
        self.setupEntityRatings()


    @property
    def ratings(self):
        '''Returns the EntityRatings of all fixers and entities'''
        res=[]
        if hasattr(self, 'entityRatings'):
            for pageFixerRatings in self.entityRatings.values():
                for entityRatings in pageFixerRatings.values():
                    res.extend(entityRatings)
        return res

    
    @staticmethod
    def runCmdLine(pageFixerClassList:list=None,argv=None):
        '''
        Args:
            pageFixerList(list): a list of page fixers to apply
            argv(list): the command line arguments to use
        Returns:
            a pageFixerManager that has completed the work as specified
            in the arguments
        '''
        pageFixerManager=PageFixerManager.fromCommandLine(pageFixerClassList, argv)
        if pageFixerManager:
            pageFixerManager.workOnArgs()
        return pageFixerManager
     
    @staticmethod
    def fromCommandLine(pageFixerClassList:list=None,argv=None):
        '''
        construct a pageFixerList from the command line with the given Arguments
        '''
        cmdLine=CmdLineAble()
        cmdLine.getParser()
        cmdLine.parser.add_argument("--stats", action="store_true",
                            help="calculate and show rating statistics")
        cmdLine.parser.add_argument("--listRatings", action="store_true",
                            help="calculate and show Ratings as a list of links")
        cmdLine.parser.add_argument("--verbose", action="store_true",
                            help="shows verbose output")
        cmdLine.parser.add_argument("--fix", action="store_true",
                            help="Fix the Event pages")
        cmdLine.parser.add_argument("--force",default=False, action="store_true",
                            help="Overwrite existing files")
        cmdLine.parser.add_argument('--targetWikiTextPath', dest="targetWikiTextPath",
                            help="Path to store/update the wiki entries")
        cmdLine.parser.add_argument("--fixers", nargs='+',
                            help="Name of the fixers to apply")
        cmdLine.parser.add_argument("--listFixers", action="store_true",
                            help="List all avaliable fixers")
        cmdLine.parser.add_argument("--ccId",
                            help="Id of the ConferenceCorpus data source to use")
        cmdLine.parser.add_argument("--tableFormat",
                                help="Format the resulting table should have. E.g. mediawiki, github, table")
        cmdLine.parser.add_argument("--addRatingPage", action="store_true",
                                    help="adds a rating subpage for each entity containing the ratings of the entity")
        if argv is None:
            argv=sys.argv[1:]
        args = cmdLine.parser.parse_args(argv)
        cmdLine.initLogging(args)
        pageFixers=PageFixerManager.getAllFixers()
        if args.listFixers:
            print("Avaliable fixers:")
            res=[]
            for pageFixer in pageFixers:
                pfDesc={"name":pageFixer.__name__}
                for key in "purpose", "issue":
                    if hasattr(pageFixer, key):
                        pfDesc[key]=getattr(pageFixer,key)
                res.append(pfDesc)
            print(tabulate(tabular_data=res, headers="keys"))
            return
        if pageFixerClassList is None:
            pageFixerClassList=[]
        if args.fixers:
            pageFixersByName={pf.__name__:pf for pf in pageFixers}
            for fixer in args.fixers:
                if fixer in pageFixersByName:
                    pageFixerClassList.append(pageFixersByName.get(fixer))
        if args.verbose:
            print(f"Starting pagefixers for {args.source}")
        wikiTextPath=args.backupPath
        if not wikiTextPath and args.ccId:
            home = path.expanduser("~")
            wikiTextPath = f"{home}/.or/wikibackup/{args.ccId.replace('-backup', '')}"
        wikiFileManager=WikiFileManager(sourceWikiId=args.source,
                                        wikiTextPath=wikiTextPath,
                                        targetWikiTextPath=args.targetWikiTextPath,
                                        login=False,
                                        debug=args.debug)
        pageFixerManager=PageFixerManager(pageFixerClassList,wikiFileManager=wikiFileManager,debug=args.debug)
        for pageFixer in pageFixerManager.pageFixers.values():
            pageFixer.templateName=args.template
        pageFixerManager.args=args
        return pageFixerManager
        
    def workOnArgs(self):    
        '''
        work as specified by my arguments
        '''    
        # self.wikiFilesToWorkon=self.wikiFileManager.getAllWikiFilesForArgs(self.args)
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
            if self.args.addRatingPage:
                # add rating to rating subpage after fixers are applied
                self.getRatings(debug=self.args.debug)   # rate entities again
                self.addRatingSubPages(afterFixing=True)


    def setupEntityRatings(self):
        '''
        Generates for each fixer their EntityRating objects
        '''
        entityRatings={}
        from ormigrate.fixer import Entity
        for fixerName, fixer in self.pageFixers.items():
            eventRatings=[]
            eventSeriesRatings=[]
            if Entity.EVENT in fixer.worksOn:
                eventRatings=[EntityRating(entity=entity, fixer=fixer) for entity in self.orDataSource.eventManager.getList()]
            if Entity.EVENT_SERIES in fixer.worksOn:
                eventSeriesRatings=[EntityRating(entity=entity, fixer=fixer) for entity in self.orDataSource.eventSeriesManager.getList()]
            entityRatings[fixerName]={
                Entity.EVENT:eventRatings,
                Entity.EVENT_SERIES:eventSeriesRatings
            }
        self.entityRatings=entityRatings

    def getEventRatingsForFixer(self, fixer):
        '''Returns the EventRatings the given fixer can work on'''
        entityRatings=self.entityRatings.get(fixer.__class__.__name__)
        res=[]
        if hasattr(fixer, "worksOn"):
            for entity in fixer.worksOn:
                res.extend(entityRatings.get(entity))
        return res

    def fix(self, overwrite:bool=False):
        '''
        Fix the wikiFiles by calling the fix functions of the pageFixers
        Args:
            overwrite(bool): If True existing files might be overwritten
        '''
        for pageFixer in self.pageFixers.values():
            entityRatings=self.getEventRatingsForFixer(pageFixer)
            for entityRating in entityRatings:
                pageFixer.fix(entityRating)
        #all fixes are applied → save back to wikiText file
        for entityRating in self.ratings:
            if hasattr(entityRating.entity, "smwHandler"):
                smwHandler=entityRating.entity.smwHandler
                if isinstance(smwHandler, SMWEntity):
                    smwHandler.saveToWikiText(overwrite=overwrite)
            
    def getRatings(self,debug:bool,debugLimit:int=10):
        '''
        get the ratings for my pageFixers
        
        Args:
            debug(bool): should debug information be printed
            debugLimit(int): maximum number of debug message to be printed
        '''
        for rating in self.ratings:
            rating.rate()
                
    def getRatingCounters(self):
        '''
        get the ratingCounter
        '''
        counters={}
        for attr in ["reason","pain"]:
            counters[attr]= {}
            for fixer in self.pageFixers:
                counter = Counter()
                ratings=self.getEventRatingsForFixer(self.pageFixers.get(fixer))
                for rating in ratings:
                    if hasattr(rating, attr):   # If not rated the attr is not set and thus not included in the counters
                        counter[getattr(rating, attr)]+=1
                counters[attr][fixer]=counter
        return counters
    
    def showRatingList(self,tableFormat='table'):
        '''
        show a list of ratings
        '''
        if tableFormat is None:
            tableFormat="table"
        ratings=[rating.__dict__ for rating in self.ratings if rating.pain>=0]
        for rating in ratings:
            entity=rating.get("entity")
            if hasattr(entity, "pageTitle"):
                rating["pageTitle"]=getattr(entity, "pageTitle")
            if hasattr(entity, "url"):
                rating["url"]=getattr(entity, "url")
        mandatoryFields=[*EntityRating.getSamples()[0].keys(), "url"]
        displayRatings=LOD.filterFields(ratings, fields=mandatoryFields, reverse=True)
        print(tabulate(displayRatings, headers="keys", tablefmt=tableFormat))

        
    def showRatingStats(self): 
        '''
        show the rating statistics
        '''
        tableFormat=getattr(self.args, "tableFormat")
        if tableFormat is None:
            tableFormat="table"
        counters=self.getRatingCounters()
        fixerCounter=counters["reason"]
        print("Rating:")
        reasonTable={}
        for fixer,counter in fixerCounter.items():
            total = sum(counter.values())
            for ratingType in counter:
                ratingTypeCount=counter[ratingType]
                fixerReason=f"{ratingTypeCount:5d} ({ratingTypeCount/total*100:5.1f}%)"
                if ratingType in reasonTable:
                    reasonTable[ratingType][fixer]=fixerReason
                else:
                    reasonTable[ratingType]={"Reason":ratingType.value, fixer:fixerReason}
        print(tabulate(reasonTable.values(), headers="keys", tablefmt=tableFormat))
        fixerCounter=counters["pain"]
        painTable = {}
        for fixer, counter in fixerCounter.items():
            total = sum(counter.values())
            for pain in sorted(counter):
                painCount=counter[pain]
                fixerPain=f"{painCount:5d} ({painCount/total*100:5.1f}%)"
                if pain in painTable:
                    painTable[pain][fixer]=fixerPain
                else:
                    painTable[pain]={"Pain":f"{pain:2d}", fixer:fixerPain}
        print(tabulate(painTable.values(), headers="keys", tablefmt=tableFormat))

    def showAllRatings(self):
        for i,pageTitle in enumerate(self.ratings):
            print(f"{i+1}:{pageTitle}->{self.ratings[pageTitle]}")

    def patchEventSource(self, lookup:CorpusLookup, wikiFileManager:WikiFileManager):
        '''
        patches the EventManager and EventSeriesManager by adding wikiUser and WikiFileManager
        '''
        for lookupId in ["orclone", "orclone-backup", "or", "or-backup"]:
            orDataSource = lookup.getDataSource(lookupId)
            if orDataSource is not None:
                if lookupId.endswith("-backup"):
                    orDataSource.eventManager.wikiFileManager = wikiFileManager
                    orDataSource.eventSeriesManager.wikiFileManager = wikiFileManager
                else:
                    orDataSource.eventManager.wikiUser = wikiFileManager.wikiUser
                    orDataSource.eventSeriesManager.wikiUser = wikiFileManager.wikiUser

    @staticmethod
    def getAllFixers():
        import ormigrate
        import pkgutil
        from ormigrate.fixer import ORFixer
        pagefixers = []
        for importer, modname, ispkg in pkgutil.iter_modules(ormigrate.__path__):
            module = __import__(f"ormigrate.{modname}")
            clsmembers = inspect.getmembers(getattr(module, modname), inspect.isclass)
            pageFixer=[clazz for name, clazz in clsmembers if issubclass(clazz, (ORFixer,PageFixer)) and hasattr(clazz, 'purpose')]
            pagefixers.extend(pageFixer)
        pagefixers=list(set(pagefixers))
        return pagefixers

    def addRatingSubPages(self, overwrite:bool=True, afterFixing:bool=False):
        """
        Generate the Rating subpages
        """
        wikiFileManager=WikiFileManager(self.wikiFileManager.sourceWikiId, self.wikiFileManager.targetPath)
        # generate rating topic and property pages
        from ormigrate.EventLocationHandler import EventLocationHandler
        EventLocationHandler.generateTechnicalPages("rating", wikiFileManager, overwrite=True)
        # add rating entites
        postfix="After" if afterFixing else ""
        for ratingEntity in self.ratings:
            if ratingEntity.pain != -1:
                wikiFile=wikiFileManager.getWikiFile(f"{ratingEntity.pageTitle}/rating", checkWiki=False)
                if not wikiFile.wikiText:
                    # rating subpage does not exist → add Headline with link to original entity
                    wikiFile.wikiText=f"== Ratings for [[{ ratingEntity.pageTitle }]]=="
                rating={
                    "fixer": ratingEntity.fixer.__class__.__name__,
                    f"pain{postfix}":str(ratingEntity.pain),
                    f"reason{postfix}":str(ratingEntity.reason.value),
                    f"hint{postfix}":str(ratingEntity.hint),
                    "storemode":"subobject"
                }
                wikiFile.updateTemplate("Rating", rating, match={"fixer":ratingEntity.fixer.__class__.__name__}, prettify=True)
                wikiFile.save_to_file(overwrite=overwrite)

    
    
class PageFixer(object):
    '''
    general fixer for wiki pages
    '''

    def __init__(self,pageFixerManager:PageFixerManager,debug=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.pageFixerManager=pageFixerManager
        self.wikiFileManager=pageFixerManager.wikiFileManager

    def fixEventRecord(self):
        ''' abstract base function to be overwritten by fixing class'''
        return

    def getRatingFromWikiFile(self,wikiFile:WikiFile)->PageRating:
        '''
        Args:
            wikiFile(WikiFile): the wikiFile to work on

        Return:
            Rating: The rating for this WikiFile

        '''
        # prepare rating
        _wikiText,eventRecord,rating=self.prepareWikiFileRating(wikiFile,self.templateName)
        #      rating=Rating(6,RatingType.invalid,f"{self.__class__.__name__} has no rating implementation for {wikiFile.getPageTitle()}")
        arating=self.getRating(eventRecord)
        rating.set(arating.pain,arating.reason,arating.hint)
        return rating

    def prepareWikiFileRating(self,wikiFile,templateName=None):
        '''
        prepare the rating of an entity record directly from the wikiFile
        '''
        if templateName is None:
            templateName=self.templateName
        # get the markup
        wikiText=str(wikiFile)
        # retrieve the name/value list
        entityDict=wikiFile.extract_template(templateName)
        # retrieve the page Title
        pageTitle=wikiFile.getPageTitle()
        if entityDict:
            # convert the content according to the property lookup
            propertyLookup=self.propertyLookups[templateName]
            # create a proper entity record
            entityRecord=SMWEntity.fromWikiSonToLod(entityDict,propertyLookup)
        else:
            entityRecord={}
        # create a default bad rating
        rating=PageRating(pageTitle,templateName,7,RatingType.missing,"rating error")
        return wikiText,entityRecord,rating


    
class EntityFixer(PageFixer):
    '''
    fixer for entities
    '''
    
    def __init__(self,pageFixerManager:PageFixerManager,debug=False):
        '''
        constructor
        '''
        super(EntityFixer,self).__init__(pageFixerManager, debug)
        self.propertyLookups={}
        
    def rate(self,rating:EntityRating):
        '''
        Hollywood style callback with a prepared rating to be filled with the
        actual rating of this fixer. So the fixer needs to modify this rating accordingly.
        
        Args:
            rating(EntityRating): the rating for a single entity
        '''
        raise Exception("rate not implemented")
        pass
    
    def fix(self,rating:EntityRating):
        '''
        Hollywood style callback with a prepared rating that has already been rated.
        The fixer will provide a fixing proposal by providing a modified version of the 
        entity and potentially the corresponding WikiText.
        
        Args:
            rating(EntityRating): the rating for a single entity
        '''
        raise Exception("fix not implemented")


if __name__ == '__main__':
    PageFixerManager.runCmdLine()