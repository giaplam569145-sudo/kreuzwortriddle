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
        pass

    def new_question_created(self, question):
        """
        Reverses the answer of a new question. This is done only once when the question is created.
        """
        question.answer = question.answer[::-1]
