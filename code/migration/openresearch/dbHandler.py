from lodstorage.sql import SQLDB
class DBHandler():
    '''
    generic entity manager
    '''

    def __init__(self, entityName, primaryKey,path,debug):
        '''
        Constructor

        Args:
            entityName(string): entityType to be managed e.g. Country
            primaryKey(string): primary key to be used
        '''

        self.entityName= entityName
        self.primaryKey= primaryKey
        self.entityInfo = None
        self.debug=debug
        self.sqlDB = SQLDB(dbname=path, debug=self.debug, errorDebug=False)

    def checkTableExists(self,entityName):
        listofTables=self.sqlDB.getTableList()
        for name in listofTables:
            if name['name'] == entityName:
                return True
        return False

    def createTable(self,listOfRecords,withDrop=False,sampleRecordCount=1,failIfTooFew=True):
        """
            Create table based of  the list of Records for the Entity DB Handler
            Args:
                listOfRecords(list of Dics): Records in dicts
            Returns:
                bool: True if the operation is successful, false otherwise
        """
        try:
            self.entityInfo = self.sqlDB.createTable(listOfRecords, self.entityName, self.primaryKey,withDrop=withDrop,sampleRecordCount=sampleRecordCount,failIfTooFew=failIfTooFew)
            return True
        except Exception as e:
            if self.debug:
                print(e)
            return False

    def store(self,listOfRecords,executeMany=False,fixNone=False):
        """
        Store the list of Records for the Entity DB Handler
        Args:
            listOfRecords(list of Dics): Records in dicts
            executeMany(bool): execute many flag
        Returns:
            bool: True if the operation is successful, false otherwise
        """

        try:
            self.sqlDB.store(listOfRecords,self.entityInfo,executeMany,fixNone=fixNone)
            return True
        except Exception as e:
            if self.debug:
                raise
            return False

    def getEntityInfo(self):
        return self.entityInfo


