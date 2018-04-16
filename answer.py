#!/usr/bin/env python

import sys
sys.path.append('utility/')
from utility import *
from tfidf import TfIdfModel
from const_tree import const_tree
from pattern.en import lemma
import string


from nltk.tag.stanford import CoreNLPNERTagger
tagger = CoreNLPNERTagger(url='http://nlp02.lti.cs.cmu.edu:9000/')

from nltk.parse.corenlp import CoreNLPParser
parser = CoreNLPParser(url='http://nlp02.lti.cs.cmu.edu:9000/')

from nltk.corpus import wordnet as wn
import nltk
nltk.download('averaged_perceptron_tagger')


# define question types

YES_NO = "YES_NO"
WH = "WH"
EITHER_OR = "EITHER_OR"


# define answer strings
YES_ANSWER = "Yes."
NO_ANSWER = "No."

logger = Logger()

# uncomment this line to print debug outputs
logger.set_level(DEBUG)

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


    def _answer_binary_by_comparison(self, question, sentence):
        """
        Basic idea: for important words in the question, check if it or its synonyms
        exist in the original sentence.
        List of important words' tags:
            numbers: CD
            nouns: NN, NNS, NNP, NNPS
            verbs: VB, VBD, VBG, VBN, VBP, VBZ
            misc: FW
            adjectives: JJ, JJR, JJS
            adverbs: RB, RBR, RBS
        Policies:   
            number: check if it or its synonym exists in the original sentence
            noun:
                NN and NNS: check if it or its synonym exists in the original sentence
                NNP and NNPS: check if it exists in the original sentence
            verbs: check if it or its synonym exists in the original sentence
            misc: check if it exists in the original sentence
            adjectives and adverbs:
                check if it exists in the original sentence:
                    if yes:
                        continue
                    if no:
                        check if its antonyms exist in the original sentence:
        """
        def _check_word_existence(word, word_sets):
            return word.lower() in word_sets or wn.morphy(word) in word_sets or lemma(word) in word_sets

        def _check_synonyms_existence(word, word_sets, wn_pos):
            for synsets in wn.synsets(word.lower(), pos=wn_pos):
                for name in synsets.lemma_names():
                    if name in word_sets or wn.morphy(name) in word_sets or lemma(name) in word_sets:
                        return True
            return False

        def _check_antonyms_existence(word, word_sets, wn_pos):
            for le in wn.lemmas(word, pos=wn_pos):
                for antonym in le.antonyms():
                    name = antonym.name()
                    if name in word_sets or wn.morphy(name) in word_sets or lemma(name) in word_sets:
                        return True
            return False
        question = question.translate(None, string.punctuation)
        sentence = sentence.translate(None, string.punctuation)
        word_sets = set()
        for word in sentence.lower().split():
            word_sets.add(word)
            # also adds the word's base form to the sets
            word_sets.add(wn.morphy(word))
            word_sets.add(lemma(word))
        # remove None in the sets
        word_sets = word_sets - {None}
        for word, tag in nltk.pos_tag(nltk.word_tokenize(question))[1:]:
            word = word.lower()
            if tag == 'CD':
                if not _check_word_existence(word, word_sets) and \
                not _check_synonyms_existence(word, word_sets, None):
                    return NO_ANSWER
            elif tag == 'NN' or tag == 'NNS':
                if not _check_word_existence(word, word_sets) and \
                not _check_synonyms_existence(word, word_sets, wn.NOUN):
                    return NO_ANSWER
            elif tag == 'NNP' or tag == 'NNPS':
                if not _check_word_existence(word, word_sets):
                    return NO_ANSWER
            elif tag[:2] == 'VB':
                if not _check_word_existence(word, word_sets) and \
                not _check_synonyms_existence(word, word_sets, wn.VERB):
                    return NO_ANSWER
            elif tag[:2] == 'JJ':
                if not _check_word_existence(word, word_sets) and \
                not _check_synonyms_existence(word, word_sets, wn.ADJ) and \
                _check_antonyms_existence(word, word_sets, wn.ADJ):
                    return NO_ANSWER
            elif tag[:2] == 'RB':
                if not _check_word_existence(word, word_sets) and \
                not _check_synonyms_existence(word, word_sets, wn.ADV) and \
                _check_antonyms_existence(word, word_sets, wn.ADV):
                    return NO_ANSWER
        return YES_ANSWER

    def _answer_binary_question(self, question):
        most_relevant_sentence = self.tfidf.getNRelevantSentences(question, 1)[0][0]
        return self._answer_binary_by_comparison(question, most_relevant_sentence)

    def _answer_wh_question(self, question):
        # TODO Unimplemented
        return self.tfidf.getNRelevantSentences(question, 1)[0][0]

    def _answer_either_or_question(self, question):
        # TODO Unimplemented
        return self.tfidf.getNRelevantSentences(question, 1)[0][0]

    def answer_questions(self):
        for Q in self.questions:
            logger.debug("[Question] {}".format(Q))
            logger.debug("[Relevant sentence] {}".format(self.tfidf.getNRelevantSentences(Q, 1)[0][0]))

            question_type = self._get_question_type(Q)
            if question_type == None:
                continue
            if question_type == YES_NO:
                A = self._answer_binary_question(Q)
            elif question_type == WH:
                A = self._answer_wh_question(Q)
            elif question_type == EITHER_OR:
                A = self._answer_either_or_question(Q)
            else:
                # default answer
                A = self.tfidf.getNRelevantSentences(Q, 1)[0][0]

            print A

if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print "usage: ./answer article.txt questions.txt"
        sys.exit(1)
    ARTICLE_FILENAME = sys.argv[1]
    QUESTIONS_FILENAME = sys.argv[2]
    TOP_N_SENTENCES = 3 # Number of top relevant function
    A = Answer(ARTICLE_FILENAME, QUESTIONS_FILENAME)
    A.answer_questions()
