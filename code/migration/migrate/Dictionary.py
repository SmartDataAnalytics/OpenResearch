import yaml


class Dictionary(object):
    ''' a dictionary to support ordinal parsing'''

    def __init__(self, yamlPath):
        self.tokens = {}
        self.read(yamlPath)
        pass

    def searchToken(self, token):
        ''' replace the given token with it's search equivalent by removing special chars
            https://github.com/WolfgangFahl/ProceedingsTitleParser/blob/7e52b4e3eae09269464669fe387425b9f6392952/ptp/titleparser.py#L425
        '''
        search = token
        for special in ['.',',',':','[',']','"','(',')']:
            search = token.replace(special, '')
        return search

    def getToken(self, token):
        ''' check if this dictionary contains the given token
            https://github.com/WolfgangFahl/ProceedingsTitleParser/blob/7e52b4e3eae09269464669fe387425b9f6392952/ptp/titleparser.py#L432
        '''
        token = token.replace('_', ' ')  # restore blank
        search = self.searchToken(token)
        if search in self.tokens:
            dtoken = self.tokens[search]
            dtoken["label"] = search
            return dtoken
        return None

    def read(self, yamlPath=None):
        ''' read the dictionary from the given yaml path
            https://github.com/WolfgangFahl/ProceedingsTitleParser/blob/7e52b4e3eae09269464669fe387425b9f6392952/ptp/titleparser.py#L456
        '''
        if yamlPath is None:
            raise ValueError("Lookup dictionary must be defined")
        with open(yamlPath, 'r') as stream:
            self.tokens = yaml.safe_load(stream)
        pass
