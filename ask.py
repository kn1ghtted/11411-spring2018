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
from why_question import *

from adverbial_question import *

#import nltk
#nltk.download('wordnet')


logger = Logger()



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
        return None # generting binary question before
        # q = ask_binary_question(vp, np)
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

def select_questions(all, n):
    # TODO
    all_flattened = reduce(lambda x, y: x + y, all)
    return all_flattened[:n]


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

    total_types = 5
    """
    Question types:
    0: binary (lxy)
    1, 2: what, who (questions on subject or object)
    3: why question
    4: when, where, how ... (questions on adverbial)
    """

    all_questions = [[] for i in xrange(total_types)]
    generated_count = 0

    # all parsed nodes: a 2d array
    # 1st level index i : corresponds to the ith sentence being parsed
    # 2nd level index j : corresponds to the copy of the node for the jth question type
    all_parsed_nodes = []
    for sentence in sentences:
        parsed_string = str(next(parser.raw_parse(sentence)))
        nodes = []
        for typeNum in xrange(total_types):
            new_node = const_tree.to_const_tree(parsed_string)
            nodes.append(new_node)
        all_parsed_nodes.append(nodes)

    # ask binary questions
    #all_questions[0] = ask_binary_question2(sentences, num)

    for i in xrange(len(sentences)):
        for typeNum in xrange(total_types):
            root = all_parsed_nodes[i][typeNum]
            q = generate_questions(root, typeNum)
            # here might be a bug, q could be empty instead of None
            if q != None and q != "":
                generated_count += 1
                logger.debug("Generated {} questions".format(generated_count))
                all_questions[typeNum].append(q)

    final_questions = select_questions(all_questions, n_questions)
    for q in final_questions:
        print q


if __name__ == '__main__':
    run_generator()



