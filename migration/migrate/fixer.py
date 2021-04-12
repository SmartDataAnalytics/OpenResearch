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

class PageFixer(object):
    '''
    helper fixing page
    '''

    def __init__(self,wikiId="or",baseUrl="https://www.openresearch.org/wiki/",debug=False):
        '''
        Constructor
        '''
        self.wikiId = wikiId
        self.baseUrl = baseUrl
        self.debug=debug

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

    def getAllPages(self):
        '''
        get all wiki pages
        '''
        home = path.expanduser("~")
        allPages = []
        for root, dirnames, filenames in walk('%s/wikibackup/%s/' % (home,self.wikiId)):
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

        