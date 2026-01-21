import regex as re
from collections import Counter, defaultdict
def bpe(input_path, vocab_size, special_tokens):
    
    re_compiled = re.compile(special_tokens)
    # read file -> chunks
    file = open(input_path, "r", )
    chunks = re.findall(re_compiled, file)

    # file -> lists
    int_lists = []
    for chunk in chunks:
        int_list = list(chunk.encode("utf-8"))
        int_lists.append(int_list)
    
    # init pair_list
    pair_dict = defaultdict(int)
    for int_list in int_lists:
        for idx in range (len(int_list) - 1):
            pair_dict[(int_list[idx], int_list[idx + 1])] + 1


    # init vocab, merge
    vocab = {i: bytes([i]) for i in range (256)}
    current_size = 256
    merge = defaultdict(int)

    while current_size < vocab_size:
        
        best_pair = max(pair_dict, key = pair_dict.get)

        new_int_lists = []
        for int_list in int_lists:
            new_int_list = []
            idx = 0
            while idx < len(int_list):
                if idx + 1 < len(int_list) and (int_list[idx], int_list[idx + 1]) == best_pair:
                    # newlist.append(int_list[idx] + int_list[idx + 1])
                    new_int_list.append(current_size)
                    idx = idx + 1

                    # maintain pair_dict
                    if idx > 0:
                        pair_dict[(int_list[idx - 1], int_list[idx])] -= 1
                        pair_dict[(int_list[idx - 1], current_size)] += 1
                    if idx + 1 < len(int_list):
                        pair_dict[(int_list[idx + 1], int_list[idx + 2])] -= 1
                        pair_dict[(current_size, int_list[idx + 2])] += 1

                else:
                    new_int_list.append(int_list[idx])
                
                idx += 1
            new_int_lists.append(new_int_list)

        int_lists = new_int_lists

        vocab[current_size] = best_pair[1] + best_pair[2]
        merge[best_pair] = current_size

        current_size += 1
        
    return vocab, merge
