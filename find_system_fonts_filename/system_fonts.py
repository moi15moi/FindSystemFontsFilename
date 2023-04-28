from abc import ABC, abstractmethod
from typing import Set


class SystemFonts(ABC):
    @staticmethod
    @abstractmethod
    def get_system_fonts_filename() -> Set[str]:
        """
        Return an set of all the installed fonts filename.
        """
        pass
