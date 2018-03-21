from stanfordcorenlp import StanfordCoreNLP
from const_tree import const_tree
from pattern.en import lemma
import nltk
import re
import string

def text2sentences(text):
    ret = list()
    # remove non-ascii characters
    text = re.sub(r'[^\x00-\x7f]',r'', text)
    for sentence in nltk.sent_tokenize(text):
        ret += re.split('\n+', sentence)
    return ret

def generate_binary_question(sentence, aux_verbs, verb_type_aux_verb_mapping):
    question = ''
    parsed_string = nlp.parse(sentence)
    root = const_tree.to_const_tree(parsed_string)
    np = None
    verb = None
    vp_without_verb = None
    for child in root.children[0].children:
        if child.type == 'NP':
            np = child.to_string()
            np = np[0].lower()+np[1:]
        if child.type == 'VP':
            tokens = child.to_string_recur()
            verb = tokens[0]
            vp_without_verb = ' '.join(tokens[1:len(tokens)])
            verb_type = child.children[0].type
    if np == None or verb == None or verb_type == None:
        return None
    if verb in aux_verbs:
        question += string.capitalize(verb)
        question += ' ' + np + ' ' + vp_without_verb + '?'
    else:
        if verb_type not in verb_type_aux_verb_mapping:
            return None
        question += verb_type_aux_verb_mapping[verb_type]
        question += ' ' + np + ' ' + lemma(verb) + ' ' + vp_without_verb + '?'
    return question

if __name__ == '__main__':
    input_file = 'sample_input.txt'
    with open(input_file, 'r') as f:
        text = f.read()

    sentences = text2sentences(text)

    # remove sentences not ending with '.'
    sentences = [x for x in sentences if x[-1:] is '.']
    aux_verbs = {'am', 'are', 'is', 'was', 'were', 'being', 'been', 'can', \
        'could', 'dare', 'do', 'does', 'did', 'have', 'has', 'had', 'having', \
        'may', 'might', 'must', 'need', 'ought', 'shall', 'should', 'will', 'would'}
    verb_type_aux_verb_mapping = {'VB': 'Do', 'VBZ': 'Does', 'VBP': 'Do', 'VBD': 'Did'}

    nlp = StanfordCoreNLP('/home/lxy/stanford-corenlp-full-2017-06-09')

    questions = list()

    for sentence in sentences:
        question = generate_binary_question(sentence, aux_verbs, verb_type_aux_verb_mapping)
        if question is not None:
            questions.append(question)
            print question
            print '\n'

    nlp.close()