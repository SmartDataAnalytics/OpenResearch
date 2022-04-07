import argparse
import json
import sys
import warnings
from typing import Union, Type

from corpus.datasources.openresearch import OREvent, OREventSeries
from wikifile.wikiPage import WikiPage


class OrWikiPage(WikiPage):
    """
    openresearch specific version of WikiPage
    """

    def updateEvent(self, pageTitle: str, props:dict, updateMsg:str=None, denormalizeProperties:bool=True):
        """
        updates the Event WikiSON entity on the page with the given title
        Args:
            pageTitle: name of the page to update
            props(dict): values that should be used to update the WikiSon. Value None deletes a property
            updateMsg(str): update message to show in the page revisions
            denormalizeProperties(bool): update the property names to the corresponding template names. If False use names as given
        """
        if denormalizeProperties:
            props = self.normalizeProperties(record=props, entity=OREvent, reverse=True, debug=self.debug)
        self.updatePageWikiSON(pageTitle=pageTitle,
                               wikiSonEntity=OREvent.templateName,
                               props=props,
                               updateMsg=updateMsg)

    def updateEventSeries(self, pageTitle: str, props: dict, updateMsg: str, denormalizeProperties: bool = True):
        """
        updates the Event series WikiSON entity on the page with the given title
        Args:
            pageTitle: name of the page to update
            props(dict): values that should be used to update the WikiSon. Value None deletes a property
            updateMsg(str): update message to show in the page revisions
            denormalizeProperties(bool): update the property names to the corresponding template names. If False use names as given
        """
        if denormalizeProperties:
            props = self.normalizeProperties(record=props, entity=OREventSeries, reverse=True, debug=self.debug)
        self.updatePageWikiSON(pageTitle=pageTitle,
                               wikiSonEntity=OREventSeries.templateName,
                               props=props,
                               updateMsg=updateMsg)

    def getEvent(self, pageTitle:str, normalize:bool=True) -> dict:
        """
        get the event record from given page
        Args:
            pageTitle: name of the page
            normalize: If True normalize the event properties

        Returns:
            dict: event records of the page
        """
        record = self.getWikiSonFromPage(pageTitle, OREvent.templateName)
        if normalize:
            record = self.normalizeProperties(record, OREvent, force=True)
        return record

    def getEventSeries(self, pageTitle:str, normalize:bool=True) -> dict:
        """
        get the event series record from given page
        Args:
            pageTitle: name of the page
            normalize: If True normalize the event properties

        Returns:
            dict: event records of the page
        """
        record = self.getWikiSonFromPage(pageTitle, OREventSeries.templateName)
        if normalize:
            record = self.normalizeProperties(record, OREventSeries, force=True)
        return record

    @staticmethod
    def normalizeProperties(record: dict,
                            entity: Union[Type[OREvent], Type[OREventSeries]],
                            reverse: bool = False,
                            force:bool=False,
                            debug:bool=False) -> dict:
        """
        update the keys of the given record. If reverse is False normalize the given keys with the property map provided
        by the given entity. If reverse is True denormalize the keys back to the template params.

        Normalize: Acronym (template param) -> acronym (normalized param)
        Denormalize: acronym (normalized param) -> Acronym (template param)

        Args:
            record(dict): record to normalize
            entity: entity containing the template property mapping
            reverse(bool): If False normalize. Otherwise, denormalize back to template property names
            force(bool): If True include properties that are not present in the getTemplateParamLookup() of the given
                         entity. Otherwise, exclude these properties and show a warning.
            debug(bool): If True show debug messages.

        Returns:
            dict
        """
        propMap = entity.getTemplateParamLookup()
        if reverse:
            propMap = {v: k for k, v in propMap.items()}
        res = {}
        for key, value in record.items():
            if key in propMap:
                res[propMap[key]] = value
            else:
                if force:
                    res[key] = value
                else:
                    msg = f"Property '{key}' will be excluded (not present in the getTemplateParamLookup() of {entity.__name__}). To include this property use force=True"
                    warnings.warn(msg, category=Warning)
                    # if self.debug:
                    #     print(msg)
        return res

    def getPageUrl(self, pageTitle:str) -> str:
        """
        Returns the url to the given page title
        Args:
            pageTitle: name of the page

        Returns:
            str url of the page
        """
        page = self.wikiFileManager.wikiPush.fromWiki.getPage(pageTitle)
        base = page.site.site.get('base', None)
        url = base[:-len('Main_Page')] + pageTitle
        return url


def main(argv=None):
    """
    Cmdline interface for OrWikiPage
    """
    import sys
    if argv:
        sys.argv = argv
    parser = argparse.ArgumentParser(description="Edit or retrieve data event or event series data from a wiki. If no valueMap is given the entity record is returned.")
    parser.add_argument('--wikiId', required=True, help='id of the wiki')
    entityTypeChoices = {
        "Event": OREvent,
        "EventSeries": OREventSeries
    }
    parser.add_argument("-et", "--entityType", required=True,choices=entityTypeChoices.keys(), help="WikiSON type to update/query")
    parser.add_argument('-p', '--pageTitle', required=True, help='name of the page to update/query')
    parser.add_argument('-v', '--valueMap', help='properties to update the WikiSON object in JSON/dict format')
    parser.add_argument('-m', '--message', help='update message displayed in page revision')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--raw', action='store_true', help='Keep properties that can not be normalized')
    args = parser.parse_args()
    orWikiPage = OrWikiPage(wikiId=args.wikiId)
    entityType = entityTypeChoices.get(args.entityType, None)
    if args.valueMap:
        updateRecord = json.loads(args.valueMap)
        if args.debug:
            print("Update record:", updateRecord)
        if entityType == OREvent:
            orWikiPage.updateEvent(pageTitle=args.pageTitle,
                                   props=updateRecord,
                                   updateMsg=args.message)
        elif entityType == OREvent:
            orWikiPage.updateEventSeries(pageTitle=args.pageTitle,
                                         props=updateRecord,
                                         updateMsg=args.message)
        else:
            print(f"Entity type {args.entityType} not known. Update was aborted!")

    else:
        record = orWikiPage.getWikiSonFromPage(pageTitle=args.pageTitle, wikiSonEntity=entityType.templateName)
        record = orWikiPage.normalizeProperties(record, entityType, force=args.raw)
        print(record)
        return record


if __name__ == '__main__':
    sys.exit(main())