'''
Created on 06.04.2021

@author: wf
'''
from wikifile.wikiFileManager import WikiFileManager
from wikifile.cmdline import CmdLineAble
class PageFixer(CmdLineAble):
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
                self.wikiId=self.wikiClient.wikiUser.wikiId
                
    def cmdLine(self,pageFixerList:list):
        '''
        Args:
            pageFixerList(list): a list of page fixers to apply
        '''
        
    

    def fixEventRecord(self):
        '''Base function to be overwritten by fixing class'''
        return

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