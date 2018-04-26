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

    binary_question = ask_binary_question(VP, NP)[:-1] # get rid of question mark

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
Identify the or node. If it separates two non-sentence phrases,
output one of the phrases as answer
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

    def dfs(node):
        """
        DFS for "or" node
        :param node: current node
        :return: the or node
        """
        if node.word == "or":
            return node
        for child in node.children:
            ret = dfs(child)
            if ret:
                return ret

    or_node = dfs(curr)
    if or_node is None:
        logger.warning("No 'or' node found in tree!")
        return None
    print or_node

    # be_verb, ADJP, JJ_in_ADJP, ADVP, RB_in_ADVP = get_VP_components(VP)


    # reference_tokens = reference.split()

    # if (ADVP is not None) and ("or" in ADVP.to_string().split()):
    #     ADVP_tokens = ADVP.to_string().split()
    #     or_index = ADVP_tokens.index("or")
    #     if or_index < len(ADVP_tokens) - 1:
    #         A = ADVP_tokens[or_index - 1]
    #         B = ADVP_tokens[or_index + 1]
    #         if A in reference_tokens:
    #             return A + "."
    #         else:
    #             return B + "."
    #
    # # TODO: ADJP either or question
    #
    # if (ADJP is not None) and ("or" in ADJP.to_string().split()):
    #     ADJP_tokens



    return reference











