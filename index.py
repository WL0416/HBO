import sys
import getopt
import struct
import time
from util import *

'''
The parsing function, used to process the input files.
1. input_file should be the latimes file.
2. is_print will indicate if print the terms out during parsing.
3. stop_list is the file includes words which need to remove out.
'''
def parsing(input_file, is_print, stop_list):

    # some variables which used in the following logic.
    content = ''
    doc_quantity = 0
    lexicon_table_len = 0
    lexicon = []
    has_stop_list = False
    stop_hash_table = None
    hash_table_length = 0
    doc_id = 0

    # open files, set them writeable.
    # invlists needs to write in binary, so set it 'wb'
    lexicon_file = open('lexicon', 'w')
    invlists_file = open('invlists', 'wb')
    map_file = open('map', 'w')

    # if the stop list is existing, process it and create the hash table.
    if stop_list is not None:

        stop_words = (' '.join(open(stop_list).readlines())).replace('\n', ' ').strip().split()

        hash_table_length = len(max(stop_words, key=len))

        stop_hash_table = HashTable(hash_table_length)

        for stop_word in stop_words:

            stop_hash_table.add_node(stop_word, 0, False)

        has_stop_list = True

    start_parse = False
    is_content = False
    # open the source file and read the content line by line
    with open(input_file, 'r') as f:

        # loop each reading line
        for line in f:

            if not start_parse:

                if '<DOCNO>' in line:

                    map_file.write(line.strip().split()[1] + '\n')
                    doc_quantity += 1
                    start_parse = True

                else:

                    continue

            if start_parse:

                if '</TEXT>' in line:

                    content = remove_punctuation(content).lower().split()

                    temp_list = list(set(content))

                    for term in temp_list:

                        # if the arguments have stop list, use it to filter content
                        if has_stop_list:

                            index = len(term) % hash_table_length

                            stop_hash_table.check_table(term, stop_hash_table.table[index])

                            if stop_hash_table.check_result is not None:

                                continue

                        count = content.count(term)
                        indicator = term[0]
                        length = len(term)
                        visited = False

                        if lexicon_table_len < length:

                            lexicon_table_len = length

                        # use the first letter of word and
                        # the length of word to store and process the lexicon
                        for index in range(len(lexicon)):

                            if term[0] == lexicon[index].id and len(term) == lexicon[index].length:

                                if term in lexicon[index].lexicon:

                                    lexicon[index].update_term(term, doc_id, count)

                                else:

                                    lexicon[index].add_term(term, doc_id, count)

                                    # if command has -p, print term out
                                    if is_print:
                                        print(term)

                                visited = True
                                break

                        if not visited:

                            lexicon.append(TermGroup(indicator, length, term, doc_id, count))

                            # if command has -p, print term out
                            if is_print:
                                print(term)

                    is_content = False
                    start_parse = False
                    content = ''
                    doc_id += 1
                    continue

                if not is_content:

                    if '<HEADLINE>' in line or '<TEXT>' in line:

                        is_content = True

                    continue

                if is_content:

                    if '<P>' in line or '</P>' in line:

                        continue

                    if '</HEADLINE>' in line:

                        is_content = False
                        continue

                    else:
                        # put headline and text together
                        content += line.strip() + ' '

    count = 0
    # write lexicon and invlists into file
    for index in range(len(lexicon)):

        for index_each in range(len(lexicon[index].lexicon)):

            lexicon_file.write(lexicon[index].lexicon[index_each] + ' ' + str(count) + '\n')

            term_inv = lexicon[index].invlists[index_each]

            for i in term_inv:

                invlists_file.write(struct.pack('I', i))

                count += 1

            # fmt = pack_fmt(term_inv)
            # invlists_file.write(fmt + ' ')
            # invlists_file.write('R')

    map_file.write(str(doc_quantity))
    lexicon_file.write(str(lexicon_table_len))
    lexicon_file.close()
    invlists_file.close()
    map_file.close()


# punctuation removing function
def remove_punctuation(content):

    punctuations = ('.', ',', ':', ';', '?', '\"', '\'', '~', '-',
                    '!', '@', '#', '$', '%', '^', '&', '*', '(', ')',
                    '+', '=', '<', '>', '{', '}', '[', ']', '\\', '|', '/')

    for x in punctuations:

        content = content.replace(x, ' ')

    return content


def main(argv):

    is_print = False

    try:
        # get options and arguments from console command
        opts, argvs = getopt.getopt(argv, "s:p")

        # print(opts)
        # print(argvs)

    except getopt.GetoptError as error:

        print(error)

        sys.exit(2)

    input_file = argvs[0]

    stoplist = None

    for opt in opts:

        if opt[0] == '-p':

            is_print = True

        elif opt[0] == '-s':

            if opt[1] == 'stoplist' or '/home/inforet/a1/stoplist':

                pass

            else:

                print('Incorrect stoplist file.')
                sys.exit(2)

            stoplist = opt[1]

        else:

            print('Error: incorrect option.')

            break

    # start parsing doc
    parsing(input_file, is_print, stoplist)


if __name__ == "__main__":
    # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    main(sys.argv[1:])
    # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
