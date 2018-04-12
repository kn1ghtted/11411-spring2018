import unittest
from answer import Answer

class TestAnswerQuestions(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestAnswerQuestions, self).__init__(*args, **kwargs)
        ARTICLE_FILENAME = 'sample_input.txt'
        QUESTIONS_FILENAME = 'questions.txt'
        self.A = Answer(ARTICLE_FILENAME, QUESTIONS_FILENAME)

    def test_get_most_relevant_sentence(self):
        self.assertEqual(self.A.tfidf.getNRelevantSentences(\
            'Did the Artist receive highly positive reviews from critics and won many accolades?', 1)[0][0], \
            'The Artist received highly positive reviews from critics and won many accolades.'
        )
        self.assertEqual(self.A.tfidf.getNRelevantSentences(\
            'What became the most awarded French film in history?', 1)[0][0], \
            'The Artist became the most awarded French film in history.'
        )
        self.assertEqual(self.A.tfidf.getNRelevantSentences(\
            'Is the Artist a 2011 French romantic comedy-drama in the style of a black-and-white silent film?', 1)[0][0], \
            'The Artist is a 2011 French romantic comedy-drama in the style of a black-and-white silent film.'
        )

    def test_answer_binary_by_comparison(self):
        self.assertEqual(self.A._answer_binary_by_comparison(\
            'Did John eat the orange?', \
            'John ate the orange.'), \
        'Yes')
        self.assertEqual(self.A._answer_binary_by_comparison(\
            "Am I 18 years old?", \
            "I'm eighteen years old."), \
        'Yes')
        self.assertEqual(self.A._answer_binary_by_comparison(\
            "Am I 19 years old?", \
            "I'm eighteen years old."), \
        'No')
        self.assertEqual(self.A._answer_binary_by_comparison(\
            'Did the Artist receive highly positive reviews from critics and won many accolades?', \
            'The Artist received highly positive reviews from critics and won many accolades.'), \
        'Yes')
        self.assertEqual(self.A._answer_binary_by_comparison(\
            'Is the Artist a 2011 American romantic comedy-drama in the style of a black-and-white silent film?', \
            'The Artist is a 2011 French romantic comedy-drama in the style of a black-and-white silent film.'), \
        'No')
        self.assertEqual(self.A._answer_binary_by_comparison(\
            'Did the Artist receive highly positive reviews from critics and won many accolades?', \
            'The Artist received negative reviews from critics and won many accolades.'), \
        'No')

if __name__ == '__main__':
    unittest.main()