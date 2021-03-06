import getopt
import sys
import struct
from util import *
import time
import math

'''
The search function, used to search the terms one by one
'''
def search(model, query_label, num_results, lexicon, invlists, doc_map, stoplist, search_terms):

    model = model
    query_label = query_label
    num_results = num_results
    bm25_table_length = 100

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
    # get the average of document length and pop it out from the list
    avg_doc_length = int(doc_list[len(doc_list)-1][0])
    doc_list.pop()
    # get the length of table and pop it out from the list
    doc_table_length = int(doc_list[len(doc_list)-1][0])
    doc_list.pop()
    doc_hash_table = HashTable(doc_table_length)

    bm25_hash_table = HashTable(bm25_table_length)

    # construct each hash table
    for index in range(len(lexicon_list)):

        lexicon_hash_table.add_node(lexicon_list[index][0], lexicon_list[index][1], False)

    for index in range(len(doc_list)):

        doc_hash_table.add_node(index, doc_list[index], True)

    # if the stop list is existing, process it and create the hash table.
    if stoplist is not None:

        filtered_terms = []

        stop_words = (' '.join(open(stoplist).readlines())).replace('\n', ' ').strip().split()

        hash_table_length = len(max(stop_words, key=len))

        stop_hash_table = HashTable(hash_table_length)

        for stop_word in stop_words:

            stop_hash_table.add_node(stop_word, 0, False)

        for term in search_terms:

            index = len(term) % hash_table_length

            stop_hash_table.check_table(term, stop_hash_table.table[index])

            if stop_hash_table.check_result is None:

                filtered_terms.append(term)

        search_terms = filtered_terms

    # open invlists file
    inv_file = open(invlists, 'rb')

    # print('search terms ', search_terms)

    # print('total docs ', total_doc)

    for term in search_terms:

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

            inv_file.seek(index_to_inv)

            # unpack the packed data in the binary file
            quantity = struct.unpack('I', inv_file.read(4))[0]

            # how many numbers need to read
            next_bytes = quantity * 2

            fmt = str(next_bytes) + 'I'

            # unpack the following appear doc info, * 4 means the real bytes need to read
            invlist = struct.unpack(fmt, inv_file.read(next_bytes * 4))

            for index in range(len(invlist)):

                if index % 2 == 0:

                    # use doc index to find doc name from doc hash table
                    doc_index = invlist[index]
                    doc_ft = invlist[index + 1]
                    doc_num = doc_hash_table.table[doc_index].index[0]
                    doc_len = int(doc_hash_table.table[doc_index].index[1])
                    doc_weight = round(float(doc_hash_table.table[doc_index].index[2]), 3)

                    bm25_value = bm25_similarity(doc_table_length, quantity, doc_ft, doc_len, avg_doc_length)

                    bm25_index = doc_index % bm25_table_length

                    bm25_hash_table.check_table(doc_num, bm25_hash_table.table[bm25_index])

                    if bm25_hash_table.check_result:

                        bm25_hash_table.update_BM25_node(doc_num, bm25_hash_table.table[bm25_index], bm25_value, (term, doc_ft))

                    else:

                        bm25_hash_table.add_BM25_node(doc_index, doc_num, bm25_value, (term, doc_ft))

                    continue

                else:

                    pass
                    # print(str(query_label) + ' ' + doc_num + ' ' + str(invlist[index]))

    minHeap = MinHeap()

    for node in bm25_hash_table.table:

        if node.content is None:

            continue

        else:

            while True:

                minHeap.heap.append((node.content, node.BM25, node.victors))
                minHeap.minHeapify(minHeap.heap[len(minHeap.heap)-1])

                if node.next_node is not None:

                    node = node.next_node

                    continue

                else:

                    break

    result = []

    while len(minHeap.heap) > 0:

        # print('after', minHeap.heap)

        if len(minHeap.heap) <= num_results:

            result.append(minHeap.heap.pop(0))

        else:

            minHeap.heap.pop(0)

        if len(minHeap.heap) > 1:

            first_doc = minHeap.heap.pop()
            minHeap.heap.insert(0, first_doc)

            # print('before', minHeap.heap)
            minHeap.minAdjust(0)

    # print(result)

    # adjust the order of result from greater to lower
    result.reverse()

    if model == '-BM25':

        for index in range(len(result)):

            print(str(query_label) + ' ' + result[index][0] + ' ' + str(index + 1) + ' ' + str(result[index][1]))

    elif model == '-MMR':

        mmr_values = []
        first_doc = result.pop(0)
        final_result = [first_doc]
        mmr_print = []

        print(result)
        while len(result) > 0:

            for compare_doc in result:

                cos_similarity = max([cosine_similarity(compare_doc, doc) for doc in final_result])

                MMR_value = 0.7 * compare_doc[1] - 0.7 * cos_similarity

                mmr_values.append(MMR_value)

            mmr_max = max(mmr_values)

            max_index = mmr_values.index(mmr_max)

            mmr_print.append(mmr_max)

            final_result.append(result.pop(max_index))

            mmr_values = []

        for index in range(len(final_result)):

            print(str(query_label) + ' ' + final_result[index][0] +
                  ' ' + str(index + 1) + ' ' + str(final_result[index][1]) +
                  ' ' + str(mmr_print[index-1] if index > 0 else 'N/A'))

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


def bm25_similarity(N, Ft, Fdt, Ld, AL):

    k1 = 1.2
    b = 0.75

    K = k1 * ((1 - b) + (b * Ld) / AL)

    bm25 = math.log(((N - Ft + 0.5) / (Ft + 0.5))) * (((k1 + 1) * Fdt) / (K + Fdt))

    return round(bm25, 3)


def cosine_similarity(doc1, doc2):

    terms = []
    terms_in_doc1 = doc1[2]
    terms_in_doc2 = doc2[2]

    for term_doc in terms_in_doc1:

        terms.append(term_doc[0])

    for term_doc in terms_in_doc2:

        if term_doc[0] in terms:

            continue

        else:

            terms.append(term_doc[0])

    total_tf_doc1 = float(sum([tf[1] for tf in terms_in_doc1]))
    total_tf_doc2 = float(sum([tf[1] for tf in terms_in_doc2]))

    tfidf_doc1 = []
    tfidf_doc2 = []

    # print(total_tf_doc1)
    # print(total_tf_doc2)
    # print(terms)

    for term in terms:

        D = 0
        tf_doc1 = 0.0
        tf_doc2 = 0.0

        for term_doc in terms_in_doc1:

            if term == term_doc[0]:

                D += 1
                tf_doc1 = term_doc[1]/total_tf_doc1
                # print('doc1', tf_doc1)

        for term_doc in terms_in_doc2:

            if term == term_doc[0]:
                D += 1
                tf_doc2 = term_doc[1]/total_tf_doc2
                # print('doc2', tf_doc2)

        if D == 1:

            idf = 0.301

        else:

            idf = 0

        # print(idf)

        tfidf_doc1.append(round(tf_doc1 * idf, 3))
        tfidf_doc2.append(round(tf_doc2 * idf, 3))

    # print(tfidf_doc1, tfidf_doc2)

    tfidf_doc1 = sum(tfidf_doc1)
    tfidf_doc2 = sum(tfidf_doc2)

    # print(tfidf_doc1, tfidf_doc2)

    if tfidf_doc1 == 0 or tfidf_doc2 == 0:

        return 0

    else:

        return (tfidf_doc1 * tfidf_doc2) / (math.sqrt(tfidf_doc1**2) * math.sqrt(tfidf_doc2**2))


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

        if argv[0] == '-BM25' or argv[0] == '-MMR':
            pass
        else:
            print("Error: lack of model option.")
            sys.exit(2)

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