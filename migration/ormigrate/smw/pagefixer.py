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
    
    def __init__(self,pageFixerClassList,wikiFileManager, ccID:str="orclone-backup",debug=False):
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
        if wikiTextPath and args.ccId:
            home = path.expanduser("~")
            wikiTextPath = f"{home}/.or/wikibackup/{args.ccId}"
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
        if self.args.stats or self.args.listRatings:
            self.getRatings(debug=self.args.debug)
        if self.args.stats:
            self.showRatingStats()
        if self.args.listRatings:
            self.showRatingList()
        if self.args.fix:
            self.fix(self.args.force)

    def setupEntityRatings(self):
        '''
        Generates for each fixer their EntityRating objects
        '''
        entityRatings={}
        for fixer in self.pageFixers:
            eventRatings=[EntityRating(entity=entity) for entity in self.orDataSource.eventManager.getList()]
            eventSeriesRatings=[EntityRating(entity=entity) for entity in self.orDataSource.eventSeriesManager.getList()]
            from ormigrate.fixer import Entity
            entityRatings[fixer]={
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

    def getEntityRating(self, wikiFile:WikiFile):
        '''Returns EntityRating object for the given wikiFile'''
        smwEntity=SMWEntity(wikiFile=wikiFile)
        wikiSonRecords=wikiFile.extract_template("Event")
        if wikiSonRecords:
            records=SMWEntity.fromWikiSonToLod(wikiSonRecords, OREventManager.getPropertyLookup())
            for key, value in records.items():
                setattr(smwEntity,key, value)
            entityRating=EntityRating(entity=smwEntity)
            return entityRating
        else:
            return None

    def saveEntityRatingToWikiText(self, entityRating:EntityRating, overwrite:bool=False):
        '''
        Saves the given eventRating by applying the entity records to the wiki markup text
        Args:
            entityRating(EntityRating):
            overwrite(bool): If True existing files might be overwritten

        Returns:

        '''
        lookup,_dup=LOD.getLookup(OREventManager.propertyLookupList, "name")
        wikiSonRecords={lookup.get(key).get('templateParam'):value for key,value in entityRating.getRecord().items() if key in lookup}
        entityRating.wikiFile.add_template('Event',wikiSonRecords, overwrite=overwrite)
        entityRating.wikiFile.save_to_file(overwrite=overwrite)

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
        self.errors=[]
        self.ratings=PageRatingList()
        for pageFixer in self.pageFixers.values():
            entityRatings = self.getEventRatingsForFixer(pageFixer)
            for entityRating in entityRatings:
                try:
                    rating = pageFixer.rate(entityRating)
                except Exception as e:
                    self.errors.append({'error':e,'fixer':pageFixer,'pageTitle':wikiFile.getPageTitle()})
        if len(self.errors)>0 and debug:
            print(f"there are {len(self.errors)} errors")
            for i,errorRecord in enumerate(self.errors):
                if i>debugLimit:
                    break
                error=errorRecord["error"]
                traceback.print_tb(error.__traceback__)
                pageFixer=errorRecord["fixer"]
                pageTitle=errorRecord["pageTitle"]
                print(f"{i:3d}: error {error} for fixer {pageFixer.__class__.__name__} on pageTitle {pageTitle}")
                
    def getRatingCounters(self):
        '''
        get the ratingCounter
        '''
        counters={}
        for attr in ["reason","pain"]:
            counter=Counter()
            counters[attr]=counter
            for rating in self.ratings.getList():
                counter[rating.__dict__[attr]]+=1
        return counters
    
    def showRatingList(self,listFormat='json'):
        '''
        show a list of ratings
        '''
        if listFormat=="json":
            print(self.ratings.toJSON(limitToSampleFields=True))
        else:
            for rating in self.ratings.getList():
                print(rating)
        
    def showRatingStats(self): 
        '''
        show the rating statistics
        '''
        # TODO use list of dicts and pyLodStorage stats and tabulate options
        # to allow to transfer results to github,wiki and papers
        counters=self.getRatingCounters()
        counter=counters["reason"]
        print("Rating:")
        total=sum(counter.values())
        for ratingType in counter:
            ratingTypeCount=counter[ratingType]
            print(f"{ratingType.value}:{ratingTypeCount:5d} ({ratingTypeCount/total*100:5.1f}%)")
        counter=counters["pain"]
        total=sum(counter.values())    
        print("Pain:")
        for pain in sorted(counter):
            painCount=counter[pain]
            print(f"{pain:2d}:{painCount:5d} ({painCount/total*100:5.1f}%)")    
            
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