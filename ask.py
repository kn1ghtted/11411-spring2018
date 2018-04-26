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
from either_or_question import *

import math

#import nltk
#nltk.download('wordnet')



"""
Preprocess: get rid of sentence with subjects being pronouns

"""


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
        # binary: this is not needed, see main function before for floop
        return None

    elif questionType == 1:
        # question on NP
        return generate_wh_np_question(vp, np)
        # question on VP's NP
    elif questionType == 2:
        return generate_wh_vp_question(vp, np)
    elif questionType == 3:
        # 3: why questions
        return generate_why_question(vp, np)
    elif questionType == 4:
        # 4: adverbial questions (when, where, how)
        return generate_adverbial_question(root, vp, np)
        # 5: either or question
    else:
        return generate_either_or_question(root)

# get rid of all questions whose subject is pronoun
def select_questions(all, n):
    # flatten into 1d list
    """
    a) Extreme length: eliminate questions longer than 25 words, or shorter than 5 words
    b) Diversity:
        Question types:
        0: binary (lxy)
        %remaining: half yes half no

        1, 2: what, who (questions on subject or object)
        %20 each (%40)

        3: why question
        %20

        4: when, where, how ... (questions on adverbial)
        %20

        5: either or
        %10
    """
    for type_index in xrange(len(all)):
        questions_type = all[type_index]
        def filter_length(x):
            L = len(x.split())
            if L >= 25 or L <= 5:
                return False
            return True
        all[type_index] = list(filter(filter_length, questions_type))


    def cap_by_percentage(arr, ratio):
        num = math.floor(ratio * n)
        while len(arr) > num:
            arr.pop()
    L_before_capped = reduce(lambda x, y: x + y, all)
    L_category_length_before= map(lambda x: len(x), all)
    logger.debug("Before capping by percentage, individual length = {}".format(str(L_category_length_before)))
    cap_by_percentage(all[1], 0.2)
    cap_by_percentage(all[2], 0.2)
    cap_by_percentage(all[3], 0.2)
    cap_by_percentage(all[4], 0.2)
    cap_by_percentage(all[5], 0.1)

    L_category_length_after= map(lambda x: len(x), all)
    logger.debug("After capping by percentage, individual length = {}".format(str(L_category_length_after)))
    L = reduce(lambda x, y: x + y, all)
    # reversed to truncate all unneeded binary question
    return list(reversed(L))[:n]

def subject_is_pronoun(node):
    """
    Identity if a sentence has personal pronoun (PRP, PRP$) as subject
    :param node: const_tree node (at root) of a sentence
    :return: true if subject is pronoun
            false if subject is not pronoun, or NP is not found
    """

    NP = None
    for child in node.children[0].children:
        if child.type == "NP":
            NP = child
    if NP:
        for child in NP.children:
            if child.type in ["PRP$", "PRP"]:
                return True
    return False

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

    total_types = 6
    """
    Question types:
    0: binary (lxy)
    1, 2: what, who (questions on subject or object)
    3: why question
    4: when, where, how ... (questions on adverbial)
    5: either or
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


    ners = get_ners(sentences)
    binary_questions = ask_binary_question2([x[0] for x in all_parsed_nodes], ners)
    #merge yes no into one mixed array
    yes_questions = [x[0] for x in binary_questions]
    no_questions = [x[1] for x in binary_questions if x[1]]


    yes_index, no_index = len(yes_questions)-1, len(no_questions)-1
    while yes_index >= 0 or no_index >= 0:

        if no_index < 0:
            all_questions[0].append(yes_questions[yes_index])
            yes_index -= 1
        else:
            if no_index < yes_index:
                all_questions[0].append(yes_questions[yes_index])
                yes_index -= 1
            else:
                all_questions[0].append(no_questions[no_index])
                no_index -= 1

    for i in xrange(len(sentences)):
        logger.debug("[Sentence] {}".format(sentences[i]))
        for typeNum in xrange(total_types):
            root = all_parsed_nodes[i][typeNum]
            """
            skip sentences if:
                a) pronoun as subject or object
            """

            if subject_is_pronoun(root):
                break
            q = generate_questions(root, typeNum)
            # if q is a list, generated from adverbial questions
            if (isinstance(q, list)):
                for adv_q in q:
                    generated_count += 1
                    logger.debug("Generated {} questions".format(generated_count))
                    all_questions[typeNum].append(adv_q)
            # here might be a bug, q could be empty instead of None
            elif q != None and q != "":
                generated_count += 1
                logger.debug("[Question] {}".format(q))
                logger.debug("Generated {} questions".format(generated_count))
                all_questions[typeNum].append(q)

    final_questions = select_questions(all_questions, n_questions)

    for q in final_questions:
        q = q.replace(' ?', '?')
        q = q.replace(' ,', ',')
        q = q.replace(" 's", "'s")
        q = q.replace('-LRB- ', "(")
        q = q.replace(' -RRB-', ")")
        print q


if __name__ == '__main__':
    run_generator()



