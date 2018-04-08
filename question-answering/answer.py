import sys
sys.path.append('../utility/')
from utility import *
from tfidf import TfIdfModel
from const_tree import const_tree


from nltk.tag.stanford import CoreNLPNERTagger
tagger = CoreNLPNERTagger(url='http://nlp01.lti.cs.cmu.edu:9000/')

from nltk.parse.corenlp import CoreNLPParser
parser = CoreNLPParser(url='http://nlp01.lti.cs.cmu.edu:9000/')

# TODO by LXY
def get_relevant_sentence(N, input):
    pass

# given a sentence, return declarative form
# TODO maybe needed

def get_declarative_form(Q):
    pass


class Answer:
    def __init__(self, article_file, question_file):
        with open(article_file, 'r') as f:
            text = f.read()

        self.sentences = text2sentences(text)
        self.tfidf = TfIdfModel()
        self.tfidf.train(self.sentences)

        with open(question_file, "r") as f_question:
            questions = f_question.read()

        self.questions = text2sentences(questions)

        self.auxiliaries = {"am", "are", "is", "was", "were", "being", \
        "been", "can", "could", "dare", "do", "does", "did", "have", "has", \
        "had", "having", "may", "might", "must", "need", "ought", "shall", \
        "should", "will", "would"}
        # print self.questions

    def _sentence_to_const_tree(sentence):
        return const_tree.to_const_tree(str(next(parser.raw_parse(sentence))))

    def _isBinary(sentence):
        try:
            first_word = sentence.split()[0]
        except:
            return None
        return first_word.lower() in self.auxiliaries

    def _answer_binary_question(question):
        """
        Check if important words, their synonyms, or hypernyms exist in the
        original sentence.
        List of important words' tags:
            CD: Cardinal Number
            
        """
        most_relevant_sentence = self.tfidf.getNRelevantSentences(question, 1)[0]

        

    def _answer_wh_question(question):
        return "dummy answer"

    def answer_questions(self):
        for Q in self.questions:
            isBinary = self._isBinary(Q)
            if isBinary is None:
                continue
            if isBinary:
                A = _answer_binary_question(Q)
            else:
                A = _answer_wh_question(Q)

            print "Question: " + Q
            print "Answer: " + A

            # results0 = self.tfidf.getNRelevantSentences(Q, 2)
            # print "Sample Question: " + Q
            # print "Top 2 relevant sentences: " + str(results0)
            # print


if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print "usage: ./answer article.txt questions.txt"
        sys.exit(1)
    ARTICLE_FILENAME = sys.argv[1]
    QUESTIONS_FILENAME = sys.argv[2]
    TOP_N_SENTENCES = 3 # Number of top relevant function
    A = Answer(ARTICLE_FILENAME, QUESTIONS_FILENAME)
    A.answer_questions()
