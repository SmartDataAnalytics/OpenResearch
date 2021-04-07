'''
Created on 2021-04-06

@author: wf
'''
from lodstorage.jsonable import JSONAble, Types


class Event(object):
    '''
    I represent an Event
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    @classmethod
    def getSamples(cls):
        samplesLOD=[{
            "acronym":"ICSME 2020",
            "ordinal": 36,
            "type": "Conference",
            "subject": "Software engineering"
        }]
        return samplesLOD
    
    @classmethod
    def getSampleWikiSon(cls,mode='legacy'):
        if mode=='legacy':
            samplesWikiSon=["""{{Event
|Acronym=ICSME 2020
|Title=36th IEEE International Conference on Software Maintenance and Evolution
|Series=ICSME
|Ordinal=36th
|Type=Conference
|Field=Software engineering
|Start date=27th Sept, 2020
|End date=2020/10/03
|Homepage=https://icsme2020.github.io/
|City=Adelaide
|State=Online
|Country=Australia
|Abstract deadline=2020/05/22
|Paper deadline=28th May, 2020
|Notification=2020/08/04
|Camera ready=2020/08/25
|Has host organization=Institute of Electrical and Electronics Engineers
|Has coordinator=Sebastian Baltes
|has general chair=Christoph Treude, Hongyu Zhang
|has program chair=Kelly Blincoe, Zhenchang Xing
|has demo chair=Mario Linares Vasquez, Hailong Sun
}}"""]
        else:
            samplesWikiSon="..."
        
        return samplesWikiSon
    @classmethod
    def WikiSontoLOD(self,wiki_sample):
        property_list = wiki_sample.replace('}}', '').split('|')[1:]
        wikidict = {}
        for i in property_list:
            mapping = i.strip().split('=')
            try:
                wikidict[mapping[0]] = int(mapping[1])
            except:
                wikidict[mapping[0]] = mapping[1]
        return [wikidict]