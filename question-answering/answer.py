import sys
sys.path.append('../utility/')
from utility import *
from tfidf import TfIdfModel
from const_tree import const_tree


from nltk.tag.stanford import CoreNLPNERTagger
nerTagger = CoreNLPNERTagger(url='http://nlp01.lti.cs.cmu.edu:9000/')

from nltk.parse.corenlp import CoreNLPParser
parser = CoreNLPParser(url='http://nlp01.lti.cs.cmu.edu:9000/')



# define question types

YES_NO = "YES_NO"
WH = "WH"
EITHER_OR = "EITHER_OR"

# define key words for WH questions
WHO = "who"


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

        # the tfidf model that identifies the most relevant
        # sentence to a question
        self.tfidf = TfIdfModel()
        self.tfidf.train(self.sentences)

        with open(question_file, "r") as f_question:
            questions = f_question.read()

        self.questions = text2sentences(questions)

        # define key words for wh questions
        self.wh_words = {"what", "why", "when", "where", "how", "whose", "who", "which"}

        # define key words for YES_NO questions
        self.auxiliaries = {"am", "are", "is", "was", "were", "being", \
        "been", "can", "could", "dare", "do", "does", "did", "have", "has", \
        "had", "having", "may", "might", "must", "need", "ought", "shall", \
        "should", "will", "would"}
        # print self.questions

    def _sentence_to_const_tree(self, sentence):
        return const_tree.to_const_tree(str(next(parser.raw_parse(sentence))))

    # return question type:
    # YES_NO | WH | EITHER_OR
    def _get_question_type(self, sentence):
        try:
            first_word = sentence.split()[0]
        except:
            return None
        if first_word.lower() in self.auxiliaries:
            return YES_NO
        elif first_word.lower() in self.wh_words:
            return WH
        else:
            return EITHER_OR


    def _answer_binary_question(self, question):
        """
        Check if important words, their synonyms, or hypernyms exist in the
        original sentence.
        List of important words' tags:
            CD: Cardinal Number
            
        """
        # TODO Unimplemented

        most_relevant_sentence = self.tfidf.getNRelevantSentences(question, 1)[0]
        return most_relevant_sentence

    # find all NER tag/noun that refers to a person
    def _answer_who(self, question):
        tokens = question.split()
        for tok in tokens:
            print nerTagger.tag(tok)
        sys.exit(1)

        # TODO Unimplemented
        return self.tfidf.getNRelevantSentences(question, 1)[0]

    def _answer_wh_question(self, question):
        question_word = question.split()[0]
        if question_word == WHO:
            return self._answer_who()
        # TODO Unimplemented
        return self.tfidf.getNRelevantSentences(question, 1)[0]

    def _answer_either_or_question(self, question):
        # TODO Unimplemented
        return self.tfidf.getNRelevantSentences(question, 1)[0]

    def answer_questions(self):
        for Q in self.questions:
            question_type = self._get_question_type(Q)
            if question_type == None:
                continue
            if question_type == YES_NO:
                print "[INFO] type: binary question"
                A = self._answer_binary_question(Q)
            elif question_type == WH:
                print "[INFO] type: wh question"
                A = self._answer_wh_question(Q)
            elif question_type == EITHER_OR:
                print "[INFO] type: either or question"
                A = self._answer_either_or_question(Q)
            else:
                # default answer
                print "[INFO] type: can't determine"
                A = self.tfidf.getNRelevantSentences(Q, 1)[0]

            print "Question: ", Q
            print "Answer: ", A
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
