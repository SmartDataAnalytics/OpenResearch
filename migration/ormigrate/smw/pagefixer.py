'''
Created on 2021-04-06

@author: wf
'''
from wikifile.wikiFileManager import WikiFileManager
from wikifile.cmdline import CmdLineAble
from wikifile.wikiRender import WikiFile
from corpus.smw.topic import SMWEntity,SMWEntityList
from ormigrate.smw.rating import RatingType,PageRating, PageRatingList, EntityRating
from collections import Counter
import sys
import traceback

class PageFixerManager(object):
    '''
    manage a list of PageFixers
    '''
    
    def __init__(self,pageFixerClassList,wikiFileManager,debug=False):
        ''' 
        construct me 
        
        Args:
            pageFixerClassList(list): a list of pageFixers
        '''
        self.pageFixerClassList=pageFixerClassList
        self.pageFixers={}
        self.debug=debug
        self.wikiFileManager=wikiFileManager
        for pageFixerClass in pageFixerClassList:
            pageFixer=pageFixerClass(self)
            pageFixerClassName=pageFixerClass.__name__
            self.pageFixers[pageFixerClassName]=pageFixer
    
    @staticmethod
    def runCmdLine(pageFixerClassList:list,argv=None):
        '''
        Args:
            pageFixerList(list): a list of page fixers to apply
            argv(list): the command line arguments to use
        Returns:
            a pageFixerManager that has completed the work as specified
            in the arguments
        '''
        pageFixerManager=PageFixerManager.fromCommandLine(pageFixerClassList, argv)
        pageFixerManager.workOnArgs()
        return pageFixerManager
     
    @staticmethod
    def fromCommandLine(pageFixerClassList,argv=None):
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
        if argv is None:
            argv=sys.argv[1:]
        args = cmdLine.parser.parse_args(argv)
        cmdLine.initLogging(args)
        if args.verbose:
            print(f"Starting pagefixers for {args.source}")
        wikiFileManager=WikiFileManager(sourceWikiId=args.source,wikiTextPath=args.backupPath,login=False,debug=args.debug)
        pageFixerManager=PageFixerManager(pageFixerClassList,wikiFileManager=wikiFileManager,debug=args.debug)
        for pageFixer in pageFixerManager.pageFixers.values():
            pageFixer.templateName=args.template
        pageFixerManager.args=args
        return pageFixerManager
        
    def workOnArgs(self):    
        '''
        work as specified by my arguments
        '''    
        self.wikiFilesToWorkon=self.wikiFileManager.getAllWikiFilesForArgs(self.args)
        if self.args.debug:
            print(f"found {len(self.wikiFilesToWorkon)} pages to work on")
        if self.args.stats or self.args.listRatings:
            self.getRatings(debug=self.args.debug)
        if self.args.stats:
            self.showRatingStats()
        if self.args.listRatings:
            self.showRatingList()
            
            
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
            for wikiFile in self.wikiFilesToWorkon.values():
                try:
                    rating = pageFixer.getRatingFromWikiFile(wikiFile)
                    self.ratings.getList().append(rating)
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