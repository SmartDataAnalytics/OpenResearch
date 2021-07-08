
import sys
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from ormigrate.fixer import PageFixer
from ormigrate.issue41 import AcronymLengthFixer
from ormigrate.issue119_Ordinals import OrdinalFixer
from ormigrate.issue163 import SeriesFixer
from ormigrate.issue71 import DateFixer
from ormigrate.issue152 import AcceptanceRateFixer
from ormigrate.issue170_curation import CurationQualityChecker
from ormigrate.issue195 import BiblographicFieldFixer
from openresearch.event import EventList,Event
from ormigrate.toolbox import HelperFunctions as hf

class EventFixer(PageFixer):

    def __init__(self,fromWikiId=None,login=False,debug=False):
        self.debug = debug
        self.login = login
        self.wikiId= fromWikiId
        self.wikiUser= hf.getSMW_WikiUser(self.wikiId,save=True)
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
                    }
                    #TODO: Fix SeriesFixer as lists are already dealt with before loading
                    # "series":{
                    #     "column":"EventSeriesFixer",
                    #     "fixer": SeriesFixer
                    # }

                }



    def getEventsForPainRating(self,painrating,fixerNames=None,cache = True):
        """
        get all the Events that fall under the given pain rating
        Args:
            painrating(int): painrating scale
            fixerList(list)(Optional): Define which fixers to consider for the
                                       pain rating condition
            cache(bool): True if the eventList is to be loaded from cache
                        False for getting it from wiki directly
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
__date__ = '2020-10-31'
__updated__ = '2021-05-27'
DEBUG=False

def mainEventFix(argv=None):
    main(argv,mode='eventfix')

def main(argv=None,mode='wikipush'):
    if argv is None:
        argv = sys.argv[1:]

    program_name = mode
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = "eventfix"
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
        if mode == "eventfix":
            parser.add_argument("-l", "--login", dest="login", action='store_true',
                                help="login to source wiki for access permission")
            parser.add_argument("-s", "--source", dest="source", help="source wiki id", required=True)
            parser.add_argument("-pr", "--painRating", default=9, dest="painRating", type=int,
                                help="give the painrating number for events to get under",
                                required=True)
            parser.add_argument("-fn", "--fixerNames", dest="fixerNames", type=str, nargs='+',
                                help="List of fixers to check for rating",default=None)
        args = parser.parse_args(argv)
        if mode == 'eventfix':
            eventFixer = EventFixer(args.source)

            eventListFixed = eventFixer.getEventsForPainRating(args.painRating,fixerNames=args.fixerNames)
            eventListJson= eventListFixed.toJSON()
            print(len(eventListFixed.getList()))
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
    sys.exit(mainEventFix())

