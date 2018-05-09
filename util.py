# generate the binary pack format
def pack_fmt(number_list):
    ubyte = 255
    ushort = 65535
    fmt = ''

    for num in number_list:

        if num <= ubyte:

            # write the data with binary form into the file, B means unsigned char, 1 byte, max 255
            fmt += 'B'

        elif ubyte < num <= ushort:

            fmt += 'H'
            # H means unsigned short, 2 bytes, max 65535

        else:

            fmt += 'I'
            # I means unsigned int, 4 bytes, max 4294967295

    checkpoint = fmt[0]
    count = 0
    new_fmt = ''
    for index in range(len(fmt)):

        if fmt[index] == checkpoint:

            count += 1

        else:

            if count > 1:
                new_fmt += str(count)

            new_fmt += checkpoint

            checkpoint = fmt[index]

            count = 1

        if index == (len(fmt) - 1):

            if count > 1:
                new_fmt += str(count)

            new_fmt += checkpoint

    return new_fmt


class TermGroup:

    def __init__(self, indicator, length, term, doc_id, count):
        self.id = indicator
        self.length = length
        self.lexicon = [term]
        self.invlists = [[1, doc_id, count]]

    def add_term(self, term, doc_id, count):
        self.lexicon.append(term)
        self.invlists.append([1, doc_id, count])

    def update_term(self, term, doc_id, count):
        index = self.lexicon.index(term)
        self.invlists[index][0] += 1
        self.invlists[index].extend([doc_id, count])


class Node:

    def __init__(self, content, next_node, index):
        self.content = content
        self.next_node = next_node
        self.index = index
        self.last_node = self
        self.BM25 = 0

class HashTable:

    def __init__(self, length):

        self.table = []

        for index in range(length):
            self.table.append(Node(None, None, None))

        self.length = length

        self.check_result = None

    def add_empty_node(self):

        self.table.append(Node(None, None, None))

    def add_node(self, word, o_index, is_map):

        if not is_map:

            word_len = len(word)

        else:

            word_len = int(word)

        index = word_len % self.length

        if self.table[index].content is None:

            self.table[index].content = word
            self.table[index].index = o_index

        else:
            node = Node(word, None, o_index)
            self.table[index].last_node.next_node = node
            self.table[index].last_node = node

    def check_table(self, word, node):

        while True:

            if node.content == word:

                self.check_result = node.index

                break

            else:

                if node.next_node is None:

                    self.check_result = None
                    break

                else:

                    node = node.next_node

    def add_BM25_node(self, o_index, word, BM25):

        index = int(o_index) % self.length

        if self.table[index].content is None:

            self.table[index].content = word
            self.table[index].index = o_index
            self.table[index].BM25 = BM25

        else:

            node = Node(word, None, o_index)
            node.BM25 = BM25
            self.table[index].last_node.next_node = node
            self.table[index].last_node = node

    def update_BM25_node(self, word, node, BM25):

        while True:

            if node.content == word:

                node.BM25 += BM25

                break

            else:

                node = node.next_node


class minHeap:

    def __init__(self):

        self.heap = []
        self.heap_size = 0

    def add_node(self, doc_name, doc_BM25):

        if len(self.heap) == 0:

            self.heap.append((doc_name, doc_BM25))

