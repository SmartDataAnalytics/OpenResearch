'''
Created on 06.04.2021

@author: wf
'''
from wikifile.wikiFileManager import WikiFileManager
from wikifile.cmdline import CmdLineAble
from wikifile.wikiRender import WikiFile
from openresearch.event import OREntity,EventList,EventSeriesList
from ormigrate.rating import RatingType,PageRating
from collections import Counter
import sys
import traceback

class PageFixerManager(object):
    '''
    manage a list of PageFixers
    '''
    
    def __init__(self,pageFixerClassList,wikiFileManager):
        ''' 
        construct me 
        
        Args:
            pageFixerClassList(list): a list of pageFixers
            wikiFileManager(WikiFileManager): the wikiFile manager to use
        '''
        self.pageFixerClassList=pageFixerClassList
        self.wikiFileManager=wikiFileManager
        self.pageFixers=[]
        for pageFixerClass in pageFixerClassList:
            pageFixer=pageFixerClass(wikiFileManager=wikiFileManager)
            self.pageFixers.append(pageFixer)
    
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
        cmdLine.parser.add_argument("--verbose", action="store_true",
                            help="shows verbose output")
        if argv is None:
            argv=sys.argv[1:]
        args = cmdLine.parser.parse_args(argv)
        cmdLine.initLogging(args)
        if args.verbose:
            print(f"Starting pagefixers for {args.source}")
        wikiFileManager=WikiFileManager(sourceWikiId=args.source,wikiTextPath=args.backupPath,login=False,debug=args.debug)
        pageFixerManager=PageFixerManager(pageFixerClassList,wikiFileManager)
        for pageFixer in pageFixerManager.pageFixers:
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
        if self.args.stats:
            self.getRatings(debug=self.args.debug)
            self.showRatingStats()
            
    def getRatings(self,debug:bool,debugLimit:int=10):
        '''
        get the ratings for my pageFixers
        
        Args:
            debug(bool): should debug information be printed
            debugLimit(int): maximum number of debug message to be printed
        '''
        self.errors=[]
        self.ratings={}
        for pageFixer in self.pageFixers:
            for wikiFile in self.wikiFilesToWorkon.values():
                try:
                    rating = pageFixer.getRatingFromWikiFile(wikiFile)
                    self.ratings[wikiFile.getPageTitle()]=rating
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
            for rating in self.ratings.values():
                counter[rating.__dict__[attr]]+=1
        return counters
        
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

    def __init__(self,wikiFileManager:WikiFileManager,debug=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.wikiclient = wikiFileManager.getWikiClient()
        if 'wikiUser' in self.wikiclient.__dict__:
            if 'wikiId' in self.wikiclient.wikiUser.__dict__:
                self.wikiId=self.wikiclient.wikiUser.wikiId
        self.propertyLookups={}
        self.propertyLookups["Event"]=EventList.getPropertyLookup()
        self.propertyLookups["Event series"]=EventSeriesList.getPropertyLookup()
     
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
    
    def prepareWikiFileRating(self,wikiFile,templateName):
        '''
        prepare the rating of an entity record directly from the wikiFile
        '''
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
            entityRecord=OREntity.fromWikiSonToLod(entityDict,propertyLookup)
        else:
            entityRecord={}
        # create a default bad rating
        rating=PageRating(pageTitle,templateName,7,RatingType.missing,"rating error")
        return wikiText,entityRecord,rating

    def fixEventRecords(self, events:list):
        """
        Gets list of dicts (list of events) and tries to apply a fix
        """
        count=0
        stats={}
        for event_unfixed in events:
            event, errors = self.fixEventRecord(event_unfixed)
            if self.debug:
                print(errors)
            if errors is not None:
                for error in errors.keys():
                    if error in stats:
                        stats[error]+=1
                    else:
                        stats[error]=1
        print(stats)

    def fixEvents(self, events:list):
        '''
        apply a fix on the event list

        Args:
            events(list): list of Event objects that should be fixed
        '''
        for event in events:
            self.fixEvent(event)

    def fixEvent(self, event):
        '''
        Applies a fixer to the given event
        Args:
            event(Event):Event object
        '''
        self.fixEventRecord(event.__dict__)

    def fixFile(self, filePath, new_file_content,fixType='Fixer'):
        '''
        separate concerns of fixing/writing.
        fix the given file

        Args:
            filePath(str):path of the wiki file to be fixed
            new_file_content(str): fixed content to be replaced with old content
        '''
        fixedPath = self.getFixedPagePath(filePath,fixType)
        with open(fixedPath, mode='w') as fileWrite:
            fileWrite.write(new_file_content)

    def fixAllFiles(self, checkFunc,fixType='Fixer', *args):
        '''
            Fix all event pages for false dates and output links to unfixable pages if debug parameter is turned on
            Args:
                checkFunc(Func): Function used for getting fixed content of files.
                args(list of args): Additional arguments to pass to the checkFunc. Default Args: page, event
        '''
        for page, event in self.getAllPageTitles4Topic("Event"):
            fixed_page = checkFunc(page, event, *args)
            if fixed_page is not None:
                self.fixFile(page, fixed_page,fixType)


    def checkAllFiles(self,checkFunc,*args):
        '''
            Check all event pages for false dates and output links to unfixable pages if debug parameter is turned on
            Args:
                checkFunc(Func): Function to use to check files for errors.
                args(list of args): Additional arguments to pass to the checkFunc. Default Args: page, event
        '''
        for page, event in self.getAllPageTitles4Topic("Event"):
            checkFunc(page, event,*args)

    
    @classmethod
    def rateWithFixers(cls,pageFixerList,entity,entityRecord):
        '''
        rate the given entityRecord with the given list of pageFixers
        
        Args:
            pagerFixerList(list): the list of page Fixers to apply
            entity(object): the entity instance e.g. an Event  or EventSeries
            entityRecord(dict): the fields of the entity as a record
            
        Returns:
            errors(list): a list of errors detected
        '''
        errors=[]
        for record in pageFixerList:
            fixer=record["fixer"]
            column=record["column"]
            try:
                rating = fixer.getRating(entityRecord)
                entityRecord[column]=rating
                entityRecord.move_to_end(column,last=False) 
            except Exception as e:
                errors.append({'error':e,'fixer':fixer,'entity':entity,'record':entityRecord})
        return errors