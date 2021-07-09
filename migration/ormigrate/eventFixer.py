
import sys
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from ormigrate.fixer import PageFixer
from ormigrate.issue41_acronym import AcronymLengthFixer
from ormigrate.issue119_ordinal import OrdinalFixer
from ormigrate.issue163_series import SeriesFixer
from ormigrate.issue71_date import DateFixer
from ormigrate.issue152_acceptancerate import AcceptanceRateFixer
from ormigrate.issue170_curation import CurationQualityChecker
from ormigrate.issue195_biblographic import BiblographicFieldFixer
from ormigrate.issue166_cfp import WikiCFPIDFixer
from openresearch.event import EventList,Event
from ormigrate.toolbox import HelperFunctions as hf
from wikifile.wikiFile import WikiFile
from wikifile.wikiFileManager import WikiFileManager

class EventFixer(PageFixer):

    fixerNameListForRating= ['curation','acronym','ordinal','date','acceptancerate','biblographic']
    fixerNameListForFix = ['cfp']

    def __init__(self,fromWikiId=None,login=False,debug=False):
        self.debug = debug
        self.login = login
        self.wikiId= fromWikiId
        self.wikiUser= hf.getSMW_WikiUser(self.wikiId,save=True)
        self.wikiclient = hf.getWikiClient(self.wikiId,save=True)
        self.fixerLookup = {
                    "curation": {
                        "column": "curationPainRating",
                        "fixer": CurationQualityChecker
                     },

                    "acronym": {
                        "column": "acronymPainRating",
                        "fixer": AcronymLengthFixer
                    },

                    "ordinal": {
                        "column": "ordinalPainRating",
                        "fixer": OrdinalFixer
                     },
                    "date":{
                        "column": "datePainRating",
                        "fixer": DateFixer
                    },
                    "acceptancerate": {
                        "column": "AcceptanceRatePainRating",
                        "fixer": AcceptanceRateFixer
                    },
                    "biblographic": {
                        "column": "BiblographicFieldFixer",
                        "fixer": BiblographicFieldFixer
                    },
                    "cfp": {
                        "column": "WikiCFPIDFixer",
                        "fixer": WikiCFPIDFixer
                    },
                    #TODO: Fix SeriesFixer as lists are already dealt with before loading
                    # "series":{
                    #     "column":"EventSeriesFixer",
                    #     "fixer": SeriesFixer
                    # }

                }

    def fixEventForWikiCFPID(self, backup= True):
        """
        Applies the WikiCFPID fixer corresponding to issue163 on OR.
        Args:
            Optional:
            backup(bool):True if backup files are to be used for fix
                         False if events should be loaded from the wiki directly
        """

        wikiFileManger= WikiFileManager(self.wikiId)
        wikiCfpFixer = WikiCFPIDFixer(self.wikiclient)
        wikiFiles = []
        if backup:
            for page, event in wikiCfpFixer.getAllPageTitles4Topic():
                wikiFile = wikiCfpFixer.fixEventFile(page, event)
                if wikiFile is not None:
                    #fixedEvent.save_to_file() ToDO: Decide if backup will be updated or directly the wiki will be updated
                    wikiFiles.append(wikiFile)
        else:
            eventList = EventList()
            eventList.fromWiki(self.wikiUser)
            for event in eventList.getList():
                wikiFile = wikiCfpFixer.fixEventFileFromWiki(event.pageTitle)
                if wikiFile is not None:
                    wikiFiles.append(wikiFile)
        wikiFileManger.pushWikiFilesToWiki(wikiFiles)



    def getEventsForPainRating(self,painrating,fixerNames=None,cache = True):
        """
        get all the Events that fall under the given pain rating
        Args:
            painrating(int): painrating scale
            fixerList(list)(Optional): Define which fixers to consider for the
                                       pain rating condition
            cache(bool): True if the eventList is to be loaded from cache
                        False for getting it from wiki directly
        Returns:
            eventListRefined(EventList): EventList with all events with painrating value >= painrating
        """
        LoDEvents=[]
        fixerList=None
        eventList = EventList()
        if fixerNames is not None:
            fixerList= []
            for fixerName in fixerNames:
                fixerList.append(self.fixerLookup[fixerName])
        if cache:
            eventList.fromCache(self.wikiUser)
        else:
            eventList.fromWiki(self.wikiUser)
        for event in eventList.getList():
            eventRecord = event.__dict__
            rateCheck= Event.rateMigration(event,eventRecord,pageFixerList=fixerList,limit=painrating)
            if rateCheck is not None:
                LoDEvents.append(eventRecord)
                if self.debug:
                    print(eventRecord)
        eventListRefined = EventList()
        eventListRefined.fromLoD(LoDEvents)
        return eventListRefined

__version__ = "0.4.8"
__date__ = '2021-07-07'
__updated__ = '2021-05-27'
DEBUG=False

def mainEventCount(argv=None):
    main(argv,mode='eventcount')

def mainEventFix(argv=None):
    main(argv, mode='eventfix')

def main(argv=None,mode='eventfix'):
    if argv is None:
        argv = sys.argv[1:]

    program_name = mode
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "eventfixer"
    user_name = "Musaab Khan"
    program_license = '''%s

      Created by %s on %s.
    ''' % (program_shortdesc, user_name, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-d", "--debug", dest="debug", action="store_true",
                            help="set debug level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        if mode == "eventcount":
            parser.add_argument("-s", "--source", dest="source", help="source wiki id", required=True)
            parser.add_argument("-pr", "--painRating", default=9, dest="painRating", type=int,
                                help="give the painrating number for events to get under. [default: %(default)s]",
                                required=True)
            parser.add_argument("-ic", "--ignoreCache", dest="ignoreCache", action="store_true",
                                help="set to get data directly from the source wiki and ignore cache [default: %(default)s]")
            parser.add_argument("-fn", "--fixerNames", dest="fixerNames", type=str, nargs='+',
                                help="List of fixers to check for rating  [default: %(default)s]",default=EventFixer.fixerNameListForRating)
        elif mode == 'eventfix':
            parser.add_argument("-s", "--source", dest="source", help="source wiki id", required=True)
            parser.add_argument("-fn", "--fixerNames", dest="fixerNames", type=str, nargs='+',
                                help="List of fixers to check for rating  [default: %(default)s]",
                                default=EventFixer.fixerNameListForFix,required='True')
            parser.add_argument("-ic", "--ignoreCache", dest="ignoreCache", action="store_true",
                                help="set to get data directly from the source wiki and ignore cache [default: %(default)s]")
        args = parser.parse_args(argv)
        if mode == 'eventcount':
            eventFixer = EventFixer(args.source)

            eventListFixed = eventFixer.getEventsForPainRating(args.painRating,fixerNames=args.fixerNames,cache=not args.ignoreCache)
            # eventListJson= eventListFixed.toJSON() #added for future requirement if applicable.
            print(len(eventListFixed.getList()))
        elif mode == 'eventfix':
            if 'cfp' in args.fixerNames:
                eventFixer = EventFixer(args.source)
                eventFixer.fixEventForWikiCFPID(backup=not args.ignoreCache)
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 1
    except Exception as e:
        if DEBUG:
            raise (e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-d")
    sys.exit(mainEventCount())

