# Simple usage
from stanfordcorenlp import StanfordCoreNLP
# import nltk
import re
import json
import os

# nlp = StanfordCoreNLP('/home/lxy/stanford-corenlp-full-2017-06-09')

# sentence = 'Guangdong University of Foreign Studies is located in Guangzhou.'
# print 'Tokenize:', nlp.word_tokenize(sentence)
# print 'Part of Speech:', nlp.pos_tag(sentence)
# print 'Named Entities:', nlp.ner(sentence)
# print 'Constituency Parsing:', nlp.parse(sentence)
# print 'Dependency Parsing:', nlp.dependency_parse(sentence)

# nlp.close() # Do not forget to close! The backend server will consume a lot memery.



# def text2sentences(text):
#     ret = list()
#     # remove non-ascii characters
#     text = re.sub(r'[^\x00-\x7f]',r'', text)
#     for sentence in nltk.sent_tokenize(text):
#         ret += re.split('\n+', sentence)
#     return ret
#
# input_file = "/home/lxy/11611/11411-spring2018/qg-exercise/sample_input.txt"
# with open(input_file, 'r') as f:
#     text = f.read()
#
# sentences = text2sentences(text)
# sentences = [x for x in sentences if x[-1:] is '.']


#STANFORDNLP_PATH = '/home/lxy/stanford-corenlp-full-2017-06-09'
STANFORDNLP_PATH = "/Users/teddyding/11411/stanford-corenlp-full-2018-01-31"

nlp = StanfordCoreNLP(STANFORDNLP_PATH)
sentence = 'The Artist is a 2011 French romantic comedy-drama in the style of a black-and-white silent film.'
tokens = nlp.word_tokenize(sentence)
pos = nlp.pos_tag(sentence)
tree = nlp.parse(sentence)

props={'annotators': 'pos,parse','pipelineLanguage':'en','outputFormat':'json'}
tree = nlp.annotate(sentence, properties=props)
tree = json.loads(tree)
print json.dumps(tree, sort_keys=True, indent=2, separators=(',', ': '))
nlp.close()


os.environ['STANFORD_PARSER'] = '/home/lxy/stanford-corenlp-full-2017-06-09'
os.environ['STANFORD_MODELS'] = '/home/lxy/stanford-corenlp-full-2017-06-09'
parser = StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")