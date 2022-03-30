from pathlib import Path
from typing import List


class Curator:
    """
    openresearch curator
    """

    @classmethod
    def getAll(cls, filePath:str=None) -> List[str]:
        """
        get all curator names as list
        Expected file structure: curator_1\ncurator_2\ncurator_3\n

        Args:
            filePath: Location the curators file. Default location ~/.or/curators.txt

        Returns:
            list of the curator names
        """
        if filePath is None:
            curatorsFile = Path.joinpath(Path.home(), ".or", "curators.txt")
        else:
            curatorsFile = Path(filePath)
        curators = []
        if curatorsFile.is_file():
            with open(curatorsFile, mode="r") as fp:
                for line in fp.readlines():
                    if line.endswith("\n"):
                        line = line[:-len("\n")]
                    curators.append(line)
        return curators
