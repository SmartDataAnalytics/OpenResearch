'''
Created on 06.04.2021

@author: wf
'''

import os
from os import walk,path
import re
from fnmatch import filter
from sys import stdin
import ntpath
import wikitextparser as wtp
from wikibot.wikiclient import WikiClient


class PageFixer(object):
    '''
    helper fixing page
    '''

    def __init__(self,wikiClient,debug=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.wikiclient = wikiClient
        if 'wikiUser' in self.wikiclient.__dict__:
            if 'wikiId' in self.wikiclient.wikiUser.__dict__:
                self.wikiId=wikiClient.wikiUser.wikiId

    def generateLink(self,page):
        search=r".*%s/(.*)\.wiki" % self.wikiId
        replace=r"%s\1" % self.baseUrl
        alink=re.sub(search,replace,page)
        alink=alink.replace(" ","_")
        return alink

    def getFixedPagePath(self,oldpath,fixType='Fixer'):
        oldpath
        home = path.expanduser("~")
        fixedDir = '%s/wikibackup/%s/' % (home,fixType)
        os.makedirs(fixedDir,exist_ok=True)
        return fixedDir + ntpath.basename(oldpath)

    def getAllPages(self, folderName:str=None):
        '''
        get all wiki pages
        '''
        home = path.expanduser("~")
        allPages = []
        backupPath='%s/wikibackup/%s/' % (home,self.wikiId)
        if folderName is not None:
            backupPath='%s/wikibackup/%s/' % (home,folderName)
        for root, dirnames, filenames in walk(backupPath):
            for filename in filter(filenames, '*.wiki'):
                allPages.append(path.join(root, filename))
        return allPages

    def getAllPagesFromFile(self,file=stdin):
        '''
        Args:
            file(obj): IO object to read file paths from
        Returns:
            listOfFiles(list): list of all file paths
        '''
        listOfFiles = file.readlines()
        return listOfFiles
    
    
    def getNameValue(self,element,dostrip=True,separator="="):
        '''
        get a name value pair from a wikison element like |a=b
        
        Args:
            element(str): the element to check
            strip(bool): should spaces be removed
            separator(str): the separator - default is "="
        
        Returns:
            name(str): the name
            value(str): the value
        '''
        if element.startswith("|"):
            parts = element[1:].split(separator,1)
            if len(parts)==2:
                name=parts[0]
                value=parts[1]
                if dostrip:
                    value=value.strip()
                if len(value) == 0:
                    return name,None
                return name,value
        return None,None

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

    def getAllPageTitles4Topic(self,topicName="Event"):
        '''
        get all pages for the given topicName
        
        Args:
            topicName(str): the topic to "query" for
            
        Returns:
            list: the list of pageTitles
        '''
        for page in self.getAllPages():
            with open(page,'r') as f:
                event =f.read()
                wikison="{{%s" % topicName
                if wikison in event:
                    yield page,event

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


class WikiPage(object):
    '''
    Wrapper class for WikiText
    https://github.com/tholzheim/wikirender/blob/master/wikifile/wikiFile.py
    ToDo: If WikiPage works correctly in wikirender replace this class with the wikirender one
    '''

    def __init__(self, page):
        self.wikiText=wtp.parse(page)

    def get_template(self, template_name: str):
        if self.wikiText is None or self.wikiText.templates is None:
            # Wikifile has no templates
            return None
        for template in self.wikiText.templates:
            name = WikiPage.get_template_name(template.name)
            if name == WikiPage.get_template_name(template_name):
                return template
        return None

    @staticmethod
    def get_template_name(template_name: str):
        name = template_name.replace('\n', '')
        name = name.lstrip()
        name = name.rstrip()
        return name

    def extract_template(self, name: str):
        """
        Extracts the template data and returns it as dict
        Args:
            name: name of the template that should be extracted
        Returns:
            Returns template content as dict
        """
        template = self.get_template(name)
        if template is None:
            return None
        res = {}
        for arg in template.arguments:
            val=arg.value.strip()
            value = val if not val.endswith("\n") else val[:-1]
            res[arg.name.strip()] = value
        return res
