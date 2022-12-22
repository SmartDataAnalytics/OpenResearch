from typing import Dict, List, Union
from wikibot3rd.pagehistory import PageHistory
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

    @staticmethod
    def getFirstUserMatching(pageHistory:PageHistory,
                             reverse:bool=False,
                             limitedUserGroup:List[str]=None,
                             blackList:List[str]=None
                             ) -> Union[str, None]:
        """
        Returns the first user in the revisions

        Args:
            reverse(bool): If False start the search at the oldest entry. Otherwise, search from the newest to the oldest revision
            limitedUserGroup(list): limit the search to the given list. If None all users will be considered.

        Returns:
            str username that matches the search criterion
        """
        revisions = pageHistory.revisions
        revisions.sort(key=lambda r: int(getattr(r, "revid",0)))
        if reverse:
            revisions = reversed(revisions)
        for revision in revisions:
            user = getattr(revision, 'user', None)
            if user is None:
                continue
            if blackList is not None and user in blackList:
                continue
            if limitedUserGroup is None:
                return user
            elif user in limitedUserGroup:
                return user
        return None

    def getPageCreator(self) -> str:
        """

        Returns:
            str name of the pageCreator
        """
        creator = self.getFirstUserMatching(self.pageHistory, blackList=[''])
        return creator

    def getPageEditor(self, limitedUserGroup:list=None) -> str:
        """

        Returns:
            str name of the pageEditor
        """
        if limitedUserGroup is None:
            limitedUserGroup = Curator.getAll()
        editor = self.pageHistory.getFirstUser(reverse=True, limitedUserGroup=limitedUserGroup)
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
