from abc import ABC, abstractmethod

from typing import Any

class GameMode(ABC):
    """
    Abstract base class for all game modes.
    """

    @abstractmethod
    def apply(self, riddle: Any):
        """
        Applies the game mode's logic to the riddle.

        Args:
            riddle: The KreuzwortRiddle object to modify.
        """
        pass

    def new_question_created(self, question: Any):
        """
        Hook called when a new question is created, before validation.
        Allows game modes to modify a question's properties.

        Args:
            question: The Question object that was just created.
        """
        pass
