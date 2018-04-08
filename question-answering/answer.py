import sys


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
        # Read questions
        with open(question_file, "r") as F:
            self.questions = F.readlines()
            print self.questions


    def classify_question(Q, self):
        return


if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print "usage: ./answer article.txt questions.txt"
        sys.exit(1)
    ARTICLE_FILENAME = sys.argv[1]
    QUESTIONS_FILENAME = sys.argv[2]
    TOP_N_SENTENCES = 3 # Number of top relevant function
    A = Answer(ARTICLE_FILENAME, QUESTIONS_FILENAME)



