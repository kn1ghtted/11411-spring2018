# Simple usage
from stanfordcorenlp import StanfordCoreNLP
import nltk
import re

# nlp = StanfordCoreNLP('/home/lxy/stanford-corenlp-full-2017-06-09')

# sentence = 'Guangdong University of Foreign Studies is located in Guangzhou.'
# print 'Tokenize:', nlp.word_tokenize(sentence)
# print 'Part of Speech:', nlp.pos_tag(sentence)
# print 'Named Entities:', nlp.ner(sentence)
# print 'Constituency Parsing:', nlp.parse(sentence)
# print 'Dependency Parsing:', nlp.dependency_parse(sentence)

# nlp.close() # Do not forget to close! The backend server will consume a lot memery.

input_file = "/home/lxy/11611/11411-spring2018/qg-exercise/sample_input.txt"
with open(input_file, 'r') as f:
    text = f.read()


# remove non-ascii characters
text = re.sub(r'[^\x00-\x7f]',r'', text)

sentences = nltk.sent_tokenize(text)