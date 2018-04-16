#!/usr/bin/env python

# Fixed issues
# Conjunction in VP? Discarding for now
# NNP and NP? fixed in function "lowercase_if_needed"
# Anaylyze what "it" refers to

import sys
sys.path.append('./utility/')

from utility import *

from binary_question import *
from wh_question import *


from adverbial_question import *

#import nltk
#nltk.download('wordnet')






# If there is because in the sentence, generate question asking Why.
def generate_why_question(node, parent_NP):
    question = ""
    SBAR = None
    for child in node.children:
        if (child.type == "SBAR"):
            SBAR = child
        # Discard sentence with conjunction structure
        if (child.type == "CC"):
            return None
    if (SBAR == None or len(SBAR.children) == 0): return None
    # find if there is 'because'
    for child in SBAR.children:
        if (child.word == "because"):
            node.children.remove(SBAR)
            bi_question = ask_binary_question(node, parent_NP)
            # lower case the first letter
            if len(bi_question) > 0:
                bi_question = bi_question[0].lower() + bi_question[1:]
            question += "Why "
            question += bi_question
            break
    return question


def generate_questions(root, questionType):
    """

    :param root:
    :param questionType:
    :return: question
    """
    np = None
    vp = None
    for child in root.children[0].children:
        if child.type == 'NP':
            np = child
        if child.type == 'VP':
            vp = child

    if np == None or vp == None:
        return None
    # case on VP
    if questionType == 0:
        # binary
        q = ask_binary_question(vp, np)
    elif questionType == 1:
        # question on NP
        return generate_wh_np_question(vp, np)
        # question on VP's NP
    elif questionType == 2:
        return generate_wh_vp_question(vp, np)
    elif questionType == 3:
        # 3: why questions
        return generate_why_question(vp, np)
    else:
        # 4: adverbial questions (when, where, how)
        return generate_adverbial_question(root)

def run_generator():
    try:
        input_file = sys.argv[1]
        n_questions = int(sys.argv[2])
    except:
        print "./ask article.txt [nquestions]"
        sys.exit(1)

    with open(input_file, 'r') as f:
        text = f.read()

    sentences = text2sentences(text)

    # remove sentences not ending with '.'

    sentences = [x for x in sentences if x[-1:] is '.']

    questions = list()

    total_types = 5
    """
    Question types:
    0: binary (lxy)
    1, 2: what, who (questions on subject or object)
    3: why question
    4: when, where, how ... (questions on adverbial)
    """
    total_questions = 0

    for sentence in sentences:
        parsed_string = str(next(parser.raw_parse(sentence)))
        for typeNum in xrange(total_types):

            root = const_tree.to_const_tree(parsed_string)
            q = generate_questions(root, typeNum)
            # here might be a bug, q could be empty instead of None
            if q != None and q!="":
                questions.append(q)
                total_questions += 1
                print q
            if (total_questions >= n_questions):
                return


if __name__ == '__main__':
    run_generator()



