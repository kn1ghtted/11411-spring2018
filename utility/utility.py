import nltk
import re
import string
from collections import defaultdict

from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

def text2sentences(text):
    ret = list()
    # remove non-ascii characters
    text = re.sub(r'[^\x00-\x7f]',r'', text)
    for sentence in nltk.sent_tokenize(text):
        ret += re.split('\n+', sentence)
    return ret

def text2sentencesWithRanking(text):
    """
    return a list of ranked sentences
    return type: list of strs

    ranking method:
    1. Calculate the frequencies of words that are not stop words
    2. For each sentence, calculate its ranking score:
        a. For each non-stop word, add its frequency to the sentence's score
        b. Normalize the score by dividing the score by the total number of non-stop words.
           This normalization is to eliminate bias towards long sentences.
    3. Rank the sentences according to their scores
    """
    stopWords = set(stopwords.words('english'))
    sentences = list()
    # remove non-ascii characters
    text = re.sub(r'[^\x00-\x7f]',r'', text)
    for sentence in nltk.sent_tokenize(text):
        sentences += re.split('\n+', sentence)
    wordFre = defaultdict(int)
    for sentence in sentences:
        words = sentence.translate(None, string.punctuation).lower().split()
        for word in words:
            if word not in stopWords:
                wordFre[word] += 1
    sentencesWithScores = list()
    for sentence in sentences:
        words = sentence.translate(None, string.punctuation).lower().split()
        score = 0.0
        validLen = 0
        for word in words:
            if word not in stopWords:
                score += wordFre[word]
                validLen += 1
        score /= validLen
        sentencesWithScores.append((sentence, score))    
    return [x[0] for x in sorted(sentencesWithScores, key=lambda x:x[1], reverse=True)]


def lowercase_if_needed(parent_NP):
    """
    Lower case the NP in the top level, if needed (when it's not a proper noun)
    :param parent_NP:
    :return:
    """
    if parent_NP.children[0].type.startswith("NNP"):
        return parent_NP.to_string()
    if parent_NP.to_string() == "I":
        return "I"
    else:
        tokens = parent_NP.to_string_recur()
        return " ".join([tokens[0].lower()] + tokens[1:])

def get_word_supersenses(w):
    """
    return all possible supersenses for a word
    return type: set
    get the lexname/supersense of the word

    E.G.: Input: get_word_supersenses("Tom")
    Output: set(['noun.animal', 'noun.person'])

    All type: ['adj.all', 'adj.pert', 'adv.all', 'noun.Tops', 'noun.act', 'noun.animal',
    'noun.artifact', 'noun.attribute', 'noun.body', 'noun.cognition', 'noun.communication',
    'noun.event', 'noun.feeling', 'noun.food', 'noun.group', 'noun.location', 'noun.motive',
     'noun.object', 'noun.person', 'noun.phenomenon', 'noun.plant', 'noun.possession',
    'noun.process', 'noun.quantity', 'noun.relation', 'noun.shape', 'noun.state',
    'noun.substance', 'noun.time', 'verb.body', 'verb.change', 'verb.cognition',
     'verb.communication', 'verb.competition', 'verb.consumption', 'verb.contact',
    'verb.creation', 'verb.emotion', 'verb.motion', 'verb.perception', 'verb.possession',
    'verb.social', 'verb.stative', 'verb.weather', 'adj.ppl']
    """
    synsets = wn.synsets(w)
    if len(synsets) == 0:
        return set([])
    return set([s.lexname().encode("utf-8") for s in synsets])

DEBUG = 0
INFO = 1
WARNING = 2

class Logger:
    """
    A class to handle debug outputs to STDOUT
    """
    def __init__(self):
        self.level = WARNING

    def set_level(self, _level):
        self.level = _level

    def warning(self, s):
        print "[WARNING]", s

    def debug(self, s):
        if self.level <= DEBUG:
            print "[DEBUG]", s

    def info(self, s):
        if self.level <= INFO:
            print "[INFO]", s


