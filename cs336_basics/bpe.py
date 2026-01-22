import regex as re
from collections import defaultdict
from .pretokenization import find_chunk_boundaries

def bpe(input_path, vocab_size, special_tokens):
    
    # create regex
    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    # 对特殊 token 按长度降序排列，防止前缀匹配问题
    sorted_special = sorted(special_tokens, key=len, reverse=True)
    # re.escape 对特殊字符转义
    special_pattern = "|".join(re.escape(s) for s in sorted_special)
    pattern = f"{special_pattern}|{PAT}"
    re_compiled = re.compile(pattern)

    '''
    # read file -> text
    with open(input_path, "r", encoding="utf-8") as file:
        file_text = file.read()
    
    # pre_tokenization
    chunks = re.findall(re_compiled, file_text)
    '''

    # file -> lists
    # lists :: list[list[int]]
    lists = []
    '''
    for chunk in chunks:
        current_list = list(chunk.encode("utf-8"))
        lists.append(current_list)
    '''
    
    # New code using pretokenization chunking
    split_token_bytes = b"<|endoftext|>"
    if special_tokens:
        # Check if predictable special token exists
        if "<|endoftext|>" in special_tokens:
             split_token_bytes = b"<|endoftext|>"
        # Otherwise use the first one available
        elif len(special_tokens) > 0:
             split_token_bytes = special_tokens[0].encode("utf-8")

    with open(input_path, "rb") as f:
        # Use 4 chunks/processes as default
        boundaries = find_chunk_boundaries(f, 4, split_token_bytes)
        
        for start, end in zip(boundaries[:-1], boundaries[1:]):
            f.seek(start)
            # errors="ignore" used to handle potential multi-byte character splits at boundaries
            chunk_text = f.read(end - start).decode("utf-8", errors="ignore")
            
            # pre_tokenization on the chunk
            matches = re.findall(re_compiled, chunk_text)
            for match in matches:
                lists.append(list(match.encode("utf-8")))


    # init pair_list
    # pair_dict :: dict[[int, int], int]
    pair_dict = defaultdict(int)
    '''
    for current_list in lists:
        for idx in range (len(current_list) - 1):
            pair_dict[(current_list[idx], current_list[idx + 1])] += 1
    '''


    # init vocab, merge
    # vocab :: dict[int, bytes]
    # merge :: list[tuple[bytes, bytes]]
    vocab = {i: bytes([i]) for i in range (256)}
    current_size = 256
    merges = []

    while current_size < vocab_size:

        pair_dict = defaultdict(int)
        for current_list in lists:
            for idx in range (len(current_list) - 1):
                pair_dict[(current_list[idx], current_list[idx + 1])] += 1
        
        if not pair_dict:
            break
        
        # best_pair :: [int, int]
        best_pair = max(pair_dict, key = pair_dict.get) # 需要修改为最后一个
        
        new_lists = []
        vocab[current_size] = vocab[best_pair[0]] + vocab[best_pair[1]]
        for current_list in lists:
            new_current_list = []
            idx = 0
            while idx < len(current_list):
                if idx + 1 < len(current_list) and (current_list[idx], current_list[idx + 1]) == best_pair:
                    
                    new_current_list.append(current_size)
                    idx = idx + 1

                    '''
                    # maintain pair_dict
                    if idx > 0:
                        pair_dict[(current_list[idx - 1], current_list[idx])] -= 1
                        pair_dict[(current_list[idx - 1], current_size)] += 1
                    if idx + 1 < len(current_list):
                        pair_dict[(current_list[idx + 1], current_list[idx + 2])] -= 1
                        pair_dict[(current_size, current_list[idx + 2])] += 1
                    '''
                        
                else:
                    new_current_list.append(current_list[idx])
                
                idx += 1
            new_lists.append(new_current_list)

        lists = new_lists

        
        merges.append(best_pair)

        current_size += 1
        
    return vocab, merges
