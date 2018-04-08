import sys
sys.path.append('../utility/')
from utility import *
from tfidf import TfIdfModel

from nltk.tag.stanford import CoreNLPNERTagger
tagger = CoreNLPNERTagger(url='http://nlp01.lti.cs.cmu.edu:9000/')

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

        print self.questions

    def answer_questions(self):
        for Q in self.questions:

            results0 = self.tfidf.getNRelevantSentences(Q, 2)
            print "Sample Question: " + Q
            print "Top 2 relevant sentences: " + str(results0)
            print


if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print "usage: ./answer article.txt questions.txt"
        sys.exit(1)
    ARTICLE_FILENAME = sys.argv[1]
    QUESTIONS_FILENAME = sys.argv[2]
    TOP_N_SENTENCES = 3 # Number of top relevant function
    A = Answer(ARTICLE_FILENAME, QUESTIONS_FILENAME)
    A.answer_questions()



