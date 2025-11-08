from gamemode import GameMode

class ThemeBasedRiddle(GameMode):
    """
    Game mode for theme-based riddles.
    """

    def __init__(self, theme):
        self.theme = theme

    def apply(self, riddle):
        """
        Applies the theme-based logic to the riddle.
        """
        riddle.questions = [
            q for q in riddle.questions if self.theme.lower() in q.question_text.lower()
        ]


class NumberRiddle(GameMode):
    """
    Game mode for number-based riddles.
    """

    def apply(self, riddle):
        """
        Allows numbers in the answers.
        """
        pass

    def new_question_created(self, question):
        """
        Allows numbers in the answers for new questions.
        """
        question.allow_numbers = True


class ReverseRiddle(GameMode):
    """
    Game mode for reverse riddles.
    """

    def apply(self, riddle):
        """
        Reverses the answers of all questions.
        """
        for q in riddle.questions:
            q.answer = q.answer[::-1]

    def new_question_created(self, question):
        """
        No action needed for new questions.
        """
        pass
