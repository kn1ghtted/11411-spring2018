# Simple usage
from stanfordcorenlp import StanfordCoreNLP
from nltk.corpus import wordnet as wn
import nltk
import re
import json
import os
import requests
from either_or_question import *
sys.path.append("./utility/")
from utility import *
from const_tree import *
from pattern.en import lemma

# def text2sentences(text):
#     ret = list()
#     # remove non-ascii characters
# 	text = re.sub(r'[^\x00-\x7f]',r'', text)
#     for sentence in nltk.sent_tokenize(text):
#         ret += re.split('\n+', sentence)
#     return ret

STANFORD_NLP_PATH = "/Users/teddyding/11411/stanford-corenlp-full-2017-06-09"


# if __name__ == "__main__":
# input_file = "/home/lxy/11611/11411-spring2018/qg-exercise/sample_input.txt"
# with open(input_file, 'r') as f:
#     text = f.read()

# sentences = text2sentences(text)
# sentences = [x for x in sentences if x[-1:] is '.']

STANFORD_NLP_PATH = "/Users/teddyding/11411/stanford-corenlp-full-2017-06-09"


nlp = StanfordCoreNLP(STANFORD_NLP_PATH )
sentence = "In October, between the 18th and the 29th, both the Northern Taurids and the Southern Taurids are active; though the latter stream is stronger."
# sentence = "Two years later, Zimmer announces the end of production of silent films at Kinograph Studios, but Valentin is dismissive, insisting that sound is just a fad. "
tokens = nlp.word_tokenize(sentence)
pos = nlp.pos_tag(sentence)
tree = nlp.parse(sentence)
new_node = const_tree.to_const_tree(str(tree))



#
# ner = nlp.ner(sentence)
#
# print "tokenize:"
# print tokens
# print "pos_tag:"
# print pos
print "tree:"
print tree
# print "ner:"
# print ner

# print "Generated: "
# print generate_either_or_question(new_node)
# props={'annotators': 'pos,parse','pipelineLanguage':'en','outputFormat':'json'}
# tree = nlp.annotate(sentence, properties=props)
# tree = json.loads(tree)
# print json.dumps(tree, sort_keys=True, indent=2, separators=(',', ': '))
# nlp.close()
#
#
# os.environ['STANFORD_PARSER'] = '/home/lxy/stanford-corenlp-full-2017-06-09'
# os.environ['STANFORD_MODELS'] = '/home/lxy/stanford-corenlp-full-2017-06-09'
# parser = StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
#
#
# request_params = {"pattern": "(NP[$VP]>S)|(NP[$VP]>S\\n)|(NP\\n[$VP]>S)|(NP\\n[$VP]>S\\n)"}
# text = "Pusheen and Smitha walked along the beach."
# r = requests.post(url, data=text, params=request_params)
# print r.json()
#
#
# url = "http://localhost:9000/tregex"
# request_params = {"pattern": "S < (NP=np $.. (VP=vp < /VB.?/=verb))"}
# sentence = 'The Artist is a 2011 French romantic comedy-drama in the style of a black-and-white silent film.'
# r = requests.post(url, data=sentence, params=request_params)
# r = r.json()['sentences'][0]['0']['namedNodes']
# subject_tree = r[0]['np']
# vp_tree = r[1]['vp']
# verb_tree = r[2]['verb']
# print subject_tree + verb_tree + vp_tree
#
#
# print json.dumps(r.json(), sort_keys=True, indent=2, separators=(',', ': '))