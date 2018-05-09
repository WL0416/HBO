import getopt
import sys
import struct
from util import *
import time

'''
The search function, used to search the terms one by one
'''
def search(model, query_label, num_results, lexicon, invlists, doc_map, stoplist, search_terms):

    model = model
    query_label = query_label
    num_results = num_results

    start_time = int(round(time.time() * 1000))
    hash_table_length = 0
    stop_hash_table = None

    lexicon_list = doc2list(lexicon)
    doc_list = doc2list(doc_map)

    # create the lexicon hash table
    lexicon_table_length = int(lexicon_list[len(lexicon_list)-1][0])
    lexicon_list.pop()
    lexicon_hash_table = HashTable(lexicon_table_length)

    # create doc map hash table
    doc_table_length = int(doc_list[len(doc_list)-1][0])
    doc_list.pop()
    doc_hash_table = HashTable(doc_table_length)

    # construct each hash table
    for index in range(len(lexicon_list)):

        lexicon_hash_table.add_node(lexicon_list[index][0], lexicon_list[index][1], False)

    for index in range(len(doc_list)):

        doc_hash_table.add_node(index, doc_list[index], True)

    # if the stop list is existing, process it and create the hash table.
    if stoplist is not None:

        stop_words = (' '.join(open(stoplist).readlines())).replace('\n', ' ').strip().split()

        hash_table_length = len(max(stop_words, key=len))

        stop_hash_table = HashTable(hash_table_length)

        for stop_word in stop_words:

            stop_hash_table.add_node(stop_word, 0, False)

    accumulator = HashTable(0)
    accumulator.length = 100

    # loop over each searched term
    if model == '-BM25':

        for term in search_terms:

            if stoplist is not None:

                index = len(term) % hash_table_length

                stop_hash_table.check_table(term, stop_hash_table.table[index])

                if stop_hash_table.check_result is not None:

                    continue

            # calculate the index of term in lexicon hash table
            index = len(term) % lexicon_table_length

            # check hash table and find out if it is in the table
            lexicon_hash_table.check_table(term, lexicon_hash_table.table[index])

            if lexicon_hash_table.check_result is None:

                print(term + ' cannot be found.')

            else:

                # if the term is found, print it out
                # print('\n' + term)

                # here get the term's index in lexicon, times 4 to get its real location in binary file
                index_to_inv = int(lexicon_hash_table.check_result) * 4

                # open invlists file
                inv_file = open(invlists, 'rb')

                inv_file.seek(index_to_inv)

                # unpack the packed data in the binary file
                quantity = struct.unpack('I', inv_file.read(4))[0]

                print(quantity)

                # how many numbers need to read
                next_bytes = quantity * 2

                fmt = str(next_bytes) + 'I'

                # unpack the following appear doc info, * 4 means the real bytes need to read
                invlist = struct.unpack(fmt, inv_file.read(next_bytes * 4))

                doc_num = None

                for index in range(len(invlist)):

                    if index % 2 == 0:

                        # use doc index to find doc name from doc hash table
                        doc_num = doc_hash_table.table[invlist[index]].index[0]

                        continue

                    else:

                        print(doc_num + ' ' + str(invlist[index]))

    elapsed_time = int(round(time.time() * 1000)) - start_time

    print('Running time: ' + str(elapsed_time) + ' ms')

# read the document and convert it to list
def doc2list(doc):

    doc_list = []

    with open(doc, 'r') as f:

        for line in f:

            term_list = line.split()

            doc_list.append(term_list)

    return doc_list


# the argument must be fill in the command
def main(argv):

    error_message = 'Error: python search.py -BM25 -q <query-label> -n <num-results> -l ' \
                    '<lexicon> -i <invlists> -m <map> [-s <stoplist>] <queryterm-1> [<queryterm-2> ... <queryterm-N>]'
    query_label = None
    num_results = None
    lexicon = None
    invlists = None
    doc_map = None
    stoplist = None

    try:

        if argv[0] == '-BM25':
            pass
        else:
            print("Error: lack of model option.")

        opts, argvs = getopt.getopt(argv[1:], "q:n:l:i:m:s:")

        for opt in opts:

            if opt[0] == '-q':

                query_label = int(opt[1])

            elif opt[0] == '-n':

                num_results = int(opt[1])

            elif opt[0] == '-l':

                lexicon = opt[1]

            elif opt[0] == '-i':

                invlists = opt[1]

            elif opt[0] == '-m':

                doc_map = opt[1]

            elif opt[0] == '-s':

                stoplist = opt[1]

        search(argv[0], query_label, num_results, lexicon, invlists, doc_map, stoplist, argvs)

    except Exception:

        print(error_message)

        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])