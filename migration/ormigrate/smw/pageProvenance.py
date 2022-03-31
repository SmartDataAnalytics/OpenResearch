from typing import Dict
from wikibot.pagehistory import PageHistory
from ormigrate.smw.curators import Curator


class PageProvenance:
    """
    wiki page provenance
    functionality to determine the pageCreator and pageEditor
    """

    def __init__(self, wikiId: str, pageTitle: str, debug: bool = False):
        """
        Constructor

        Args:
            wikiId(str): id of the wiki
            pageTitle(str): name of the page
            debug(bool): If True show debug messages
        """
        self.debug = debug
        self.pageTitle = pageTitle
        self.wikiId = wikiId
        self.pageHistory = PageHistory(pageTitle=pageTitle, wikiId=wikiId, debug=debug)

    def getPageCreator(self) -> str:
        """

        Returns:
            str name of the pageCreator
        """
        creator = self.pageHistory.getFirstUser()
        return creator

    def getPageEditor(self) -> str:
        """

        Returns:
            str name of the pageEditor
        """
        editor = self.pageHistory.getFirstUser(reverse=True, limitedUserGroup=Curator.getAll())
        return editor

    def getProvenance(self) -> dict:
        """
        Get the provenance of the page.

        Returns:
            dict containing the pageEditor and pageCreator
        """
        provenance: Dict[str, str] = {
            "pageEditor": self.getPageEditor(),
            "pageCreator": self.getPageCreator()
        }
        return provenance
