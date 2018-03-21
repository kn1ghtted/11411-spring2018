# this file defines the data structure for constituency tree (const_tree) and provides utilities
# to convert a stanford parsing to const_tree and from const_tree to sentence


class const_tree:

    def __init__(self, type):
        self.type = type # type of this node: ROOT/N/S/NP/VP......
        self.children = [] # children nodes
        self.word = None # only when this node is a terminal (no children)

    @staticmethod
    # reads a string and returns a const_tree data structure
    def to_const_tree(string):
        # convert from unicode to ascii
        string = string.encode("utf8")
        node, index = const_tree.to_const_tree_repr(string)
        return node

    # default str function that # prints out the tree with structure
    def __str__(self):
        return self.str_recur(0)

    def str_recur(self, level):
        string = "[" + self.type + " "
        for child in self.children:
            string += "\n"
            string += "  " * (level + 1)
            string += child.str_recur(level + 1)
        if (self.word):
            string += self.word
        return string + "]"


    @staticmethod
    # recursive function for to_const_tree
    # returns the node and current index
    def to_const_tree_repr(string):
        # print "== in recursiong, string = ", repr(string)
        # assume the string starts with '('
        indices = [string.find("\n"), string.find(" ")]
        indices = [float('inf') if index == -1 else index for index in indices]
        type_end_index = min(indices)
        # print type_end_index
        type = string[1:type_end_index]
        # print "type: ", type

        node = const_tree(type)

        index = type_end_index

        while True:
            # print "New loop: ", repr(string[index:])
            # skip to the first none-space character
            while (string[index] == "\n") or (string[index] == " "):
                index += 1
            # reached end for this node
            # print "start processing: ", repr(string[index:])
            if string[index] == ")":
                return node, index
            # start of a sub node
            if string[index] == "(":
                child, sub_index = const_tree.to_const_tree_repr(string[index:])
                index = index + sub_index
                # print "-- returned from recursive call, child = ", child
                node.children.append(child)
            # word for the terminal node
            else:
                # skip to the first ')'
                start_index = index
                while (string[index] != ')'):
                    index += 1
                node.word = string[start_index:index]
                return node, index
            index += 1

        return node, index


    # convert the string at this node to tree
    def to_string(self):
        # print self.to_string_recur()

        return " ".join(self.to_string_recur())

    # helper for to_string, return list
    def to_string_recur(self):
        L = []
        for child in self.children:
            L += child.to_string_recur()
        if self.word:
            L.append(self.word)
        return L


if __name__ == "__main__":

    # tests
    import sys
    sys.path.append('../')
    from stanford_wrapper import StanfordNLP

    nlp = StanfordNLP()
    sentence = "I ate a sandwich."
    parsed_string = nlp.parse(sentence)
    # print repr(parsed_string)

    root = const_tree.to_const_tree(parsed_string)
    # print root
    # print root.to_string()
