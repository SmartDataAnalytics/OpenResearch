from ormigrate.smw.curators import Curator
from tests.basetest import ORMigrationTest
from tempfile import NamedTemporaryFile

class TestCurator(ORMigrationTest):
    """
    tests Curator
    """

    def test_getAll(self):
        """
        tests getting all curator names from curators file in ~/.or/curators.txt
        """
        return
        curators = Curator.getAll()
        if self.debug:
            print(curators)
        self.assertGreaterEqual(len(curators), 5)
        self.assertIn("Soeren", curators)

    def test_getAll_emptyFile(self):
        """
        tests getAll() if empty list is returned if file is empty
        """
        with NamedTemporaryFile() as fp:
            curators = Curator.getAll(fp.name)
            self.assertEqual([], curators)
