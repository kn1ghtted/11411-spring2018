# this file defines the data structure for constituency tree (const_tree) and provides utilities
# to convert a stanford parsing to const_tree and from const_tree to sentence

class const_tree:

    def __init__(self):
        self.type = None # type of this node: ROOT/N/S/NP/VP......
        self.children = [] # children nodes
        self.word = None # only when this node is a terminal (no children)

    @staticmethod
    # reads a string and returns a const_tree data structure
    def to_const_tree(string):
        # TODO
        return const_tree()

    # convert the string at this node to tree
    def to_string(self):
        # TODO
        return ""

