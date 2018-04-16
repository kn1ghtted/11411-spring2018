BE_VERBS = {'am', 'is', 'are', 'were', 'was'}

AUX_VERBS = {'am', 'are', 'is', 'was', 'were', 'being', 'been', 'can', \
             'could', 'dare', 'do', 'does', 'did', 'have', 'has', 'had', 'having', \
             'may', 'might', 'must', 'need', 'ought', 'shall', 'should', 'will', 'would'}

VERB_TYPE_AUX_VERB_MAPPING = {'VB': 'Do', 'VBZ': 'Does', 'VBP': 'Do', 'VBD': 'Did'}


from nltk.tag.stanford import CoreNLPNERTagger
tagger = CoreNLPNERTagger(url='http://nlp02.lti.cs.cmu.edu:9000/')

from nltk.parse.corenlp import CoreNLPParser
parser = CoreNLPParser(url='http://nlp02.lti.cs.cmu.edu:9000/')


