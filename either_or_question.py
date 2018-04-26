from statics import *
import sys
sys.path.append("./utility/")
from utility import *
from const_tree import *
import string
from binary_question import *


# map function to convert the word to "word or [antonym of word]"
def F(word, target, A):
    word = word.lower()
    if word == target:
        word += " or " + A[0]
        return word
    return word

def get_antonyms_JJ(w):
    antonyms = []
    for S in wn.synsets(w):
        # if Synset is adjective or a satellite-adj
        if S.pos() in ["a", "s"]:
            for lemma in S.lemmas():

                # if S has antonym
                if lemma.antonyms():
                    antonyms += [ant.name() for ant in lemma.antonyms()]
    return antonyms

def get_antonyms_RB(w):
    antonyms = []
    for S in wn.synsets(w):

        # if Synset is adjective or a satellite-adj
        if S.pos() in ["r"]:
            for lemma in S.lemmas():
                # if S has antonym
                if lemma.antonyms():
                    antonyms += [ant.name() for ant in lemma.antonyms()]
    return antonyms

def ask_be_verb_adjp(root, ADJP, be_verb, JJ_in_ADJP):
    """
    Ask question for sentence including [NP + be_verb + ADJP]
    :param root:
    :param ADJP:
    :param be_verb:
    :param JJ_in_ADJP:
    :return:
    """
    # get antonym of JJ
    antonyms = get_antonyms_JJ(JJ_in_ADJP.to_string())

    if len(antonyms) == 0:
        # no antonym foujd
        return None

    tokens = root.to_string().split()
    tokens_without_be_verb = list(filter(lambda x: x not in BE_VERBS, tokens))

    tokens_with_antonym = [F(token, JJ_in_ADJP.to_string(), antonyms) for token in tokens_without_be_verb]

    final_tokens = [string.capitalize(be_verb)] + tokens_with_antonym[:-1] + ["?"]

    return " ".join(final_tokens)

def ask_advp(NP, VP, ADVP, RB_in_ADVP):
    """
    Ask question for VP including adverbial phrase
    :param root:
    :param ADVP:
    :param RB_in_ADVP:
    :return:
    """

    antonyms = get_antonyms_RB(RB_in_ADVP.to_string())


    if len(antonyms) == 0:
        return None

    binary_question = ask_binary_question(VP, NP)
    if binary_question is None:
        return None

    binary_question = binary_question[:-1]# get rid of question mark

    tokens = binary_question.split()

    tokens_with_antonym = [F(token, RB_in_ADVP.to_string(), antonyms) for token in tokens]
    tokens_with_antonym[0] = string.capitalize(tokens_with_antonym[0])
    return " ".join(tokens_with_antonym + ["?"])

def get_NP_VP(node):

    NP = None
    VP = None
    # check if NP VP exists in top level
    for child in node.children:

        if child.type == "NP":
            NP = child
        elif child.type == "VP":
            VP = child
    return NP, VP

def get_VP_components(VP):
    be_verb = None
    ADJP = None
    JJ_in_ADJP = None
    ADVP = None
    RB_in_ADVP = None

    # scan for BE_VERB
    for word in VP.to_string().split():
        if word in BE_VERBS:
            be_verb = word

    for child in VP.children:

        # identify adjective phrase
        if child.type == "ADJP":
            ADJP = child
            for cc in ADJP.children:
                if cc.type == "JJ":
                    JJ_in_ADJP = cc

        # identify adverbial phrase
        if child.type == "ADVP":
            ADVP = child
            for cc in ADVP.children:
                if cc.type == "RB":
                    RB_in_ADVP = cc

    return be_verb, ADJP, JJ_in_ADJP, ADVP, RB_in_ADVP


def generate_either_or_question(root):
    NP, VP = get_NP_VP(root.children[0])

    if (NP is None) or (VP is None):
        return None

    be_verb, ADJP, JJ_in_ADJP, ADVP, RB_in_ADVP = get_VP_components(VP)


    # ask question for [be_verb] + [ADJP]


    Q = None

    if (ADJP is not None) and (be_verb is not None) and (JJ_in_ADJP is not None):
        Q = ask_be_verb_adjp(root, ADJP, be_verb, JJ_in_ADJP)

    if (ADVP is not None) and (RB_in_ADVP is not None):
        Q = ask_advp(NP, VP, ADVP, RB_in_ADVP)
    if Q:
        logger.debug("Either or question: {}".format(Q))

    return Q





"""
Identify the or node. Output the previous as well as the next node in the tree,
at the same level (this successfully handles ADVP, ADJP and other phrasal conditions)
"""
def answer_either_or_question(question, reference):
    parsed_string = str(next(parser.raw_parse(question)))
    tree = const_tree.to_const_tree(parsed_string)
    # go down and find the first SQ level
    curr = tree
    while (curr.type != "SQ"):
        if len(curr.children) == 0:
            # at the bottom but still no SQ level found
            return None
        curr = curr.children[0]

    NP, VP = get_NP_VP(curr)

    if VP is None:
        return None

    # the previous node and the next node of "or"

    def dfs(node):
        """
        DFS for "or" node
        :param node: current node
        :return: the or node
        """
        if len(node.children) == 0:
            return None, None
        p_ret, n_ret = None, None
        for child_i in xrange(len(node.children)):
            child = node.children[child_i]
            if child.word == "or":
                # return if there's no prev or next
                if (child_i == 0) or (child_i == len(node.children) - 1):
                    return None, None
                return node.children[child_i - 1], node.children[child_i + 1]
            else:
                (p, n) = dfs(child)
                if p:
                    p_ret = p
                if n:
                    n_ret = n
        return p_ret, n_ret

    or_prev, or_next = dfs(curr)

    if (or_prev is None) or (or_next is None):
        logger.warning("Can't locate or_prev, or_next!")
        return None
    logger.debug("or_prev = {}, or_next = {}".format(or_prev, or_next, ))
    A = or_prev.to_string()
    B = or_next.to_string()
    if B in reference:
        return string.capitalize(B) + "."
    else:
        return string.capitalize(A) + "."

    return reference











