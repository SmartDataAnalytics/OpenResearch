from ormigrate.smw import pageProvenance
from ormigrate.smw.pageProvenance import PageProvenance
from tests.basetest import BaseTest


class TestPageProvenance(BaseTest):
    """
    test PageProvenance
    """

    def setUp(self, debug=False, profile=True):
        super(TestPageProvenance, self).setUp(debug, profile)
        self.wikiId = "orclone"

    def test_provenance_extraction(self):
        """
        tests extracting the pageEditor and pageCreator
        """
        pageTitle = "AAAI 2021"
        pageProvenance = PageProvenance(wikiId=self.wikiId, pageTitle=pageTitle)
        pageCreator = pageProvenance.getPageCreator()
        pageEditor = pageProvenance.getPageEditor()
        if self.debug:
            print(f"{pageTitle}: pageCreator={pageCreator}, pageEditor={pageEditor}")
        # only testing for the beginning of the username for privacy reasons
        self.assertTrue(pageCreator.startswith("Ohl"))
        self.assertTrue(pageEditor.startswith("Tol"))

    def test_getProvenance(self):
        """
        tests getProvanance()
        """
        pageTitle = "AAAI 2021"
        pageProvenance = PageProvenance(wikiId=self.wikiId, pageTitle=pageTitle)
        provenance = pageProvenance.getProvenance()
        self.assertEqual(len(provenance), 2)
        self.assertIn("pageEditor", provenance)
        self.assertIn("pageCreator", provenance)
