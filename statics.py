BE_VERBS = {'am', 'is', 'are', 'were', 'was'}

AUX_VERBS = {'am', 'are', 'is', 'was', 'were', 'being', 'been', 'can', \
             'could', 'dare', 'do', 'does', 'did', 'have', 'has', 'had', 'having', \
             'may', 'might', 'must', 'need', 'ought', 'shall', 'should', 'will', 'would'}

VERB_TYPE_AUX_VERB_MAPPING = {'VB': 'Do', 'VBZ': 'Does', 'VBP': 'Do', 'VBD': 'Did'}


from nltk.tag.stanford import CoreNLPNERTagger
URL1 = "http://nlp01.lti.cs.cmu.edu:9000/"
URL2 = "http://nlp02.lti.cs.cmu.edu:9000/"
URL_LOCAL = "http://localhost:11411/"
tagger = CoreNLPNERTagger(url=URL2)

from nltk.parse.corenlp import CoreNLPParser
parser = CoreNLPParser(url=URL2)

import sys
sys.path.append("./utility/")
from utility import *

logger = Logger()
logger.set_level(NEVER)