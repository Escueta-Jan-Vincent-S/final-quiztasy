import random
import operator

class Question:
    def __init__(self):
        self.question_text = ""
        self.answer = None
        self.choices = []
        self.correct_choice = None

    def check_answer(self, user_answer):
        """Checks if the user's answer is correct"""
        return user_answer == self.answer

class MathQuestion(Question):
    def __init__(self, difficulty=1):
        super().__init__()
        self.difficulty = difficulty
        self.generate_question()

    def generate_question(self):
        """Generates a random math question based on difficulty"""
        # Select operation
        operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        }

        # Adjust ranges based on difficulty
        if self.difficulty == 1:
            num_range = (1, 10)
            ops = ['+', '-', '*']
        elif self.difficulty == 2:
            num_range = (1, 20)
            ops = ['+', '-', '*', '/']
        else:
            num_range = (1, 100)
            ops = ['+', '-', '*', '/']

        # Select operation
        op_symbol = random.choice(ops)
        operation = operations[op_symbol]

        # Generate numbers
        num1 = random.randint(*num_range)

        # For division, ensure we get clean integer results
        if op_symbol == '/':
            num2 = random.randint(1, 10)
            num1 = num2 * random.randint(1, 10)
        else:
            num2 = random.randint(*num_range)

        # Calculate answer
        result = operation(num1, num2)

        # Format answer for division to avoid long decimal places
        if op_symbol == '/':
            result = int(result)

        # Set question and answer
        self.question_text = f"What is {num1} {op_symbol} {num2}?"
        self.answer = result

        # Generate multiple choice options
        self.generate_choices()

    def generate_choices(self):
        """Generates multiple choice options"""
        self.choices = [self.answer]

        # Generate 3 wrong answers
        while len(self.choices) < 4:
            # Create wrong answers that are close to the correct one
            offset = random.randint(1, max(5, abs(self  .answer) // 2))
            if random.choice([True, False]):
                wrong_answer = self.answer + offset
            else:
                wrong_answer = self.answer - offset

            if wrong_answer not in self.choices:
                self.choices.append(wrong_answer)

        # Shuffle choices
        random.shuffle(self.choices)

        # Find the index of the correct answer
        self.correct_choice = self.choices.index(self.answer)


class QuestionGenerator:
    @staticmethod
    def get_random_question(difficulty=1):
        """Factory method to get a random question"""
        # Currently only generates math questions, but can be expanded
        return MathQuestion(difficulty)