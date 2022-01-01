# dict_no_space.txt 需要和這個程式在同一個資料夾，麻煩助教了!
class super_dict:
    def __init__(self):
        self.dict = dict()
        # every charactor has its own dictionary to connect to the next following charactor
        self.accumulate = 0
        # accumulate is used to check if the charactor is the end of the word
        # for example , when input is 白色恐 , the return value of cut_sentence need to be 2, not 3
        return

# check the charactor is english or not
def is_alphabet(uchar):
    if(uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False

# check the charactor is a punctuation or not.
def is_punc(uchar):
    if uchar == u'\u3002' or uchar == u'\uff1f' or uchar == u'\uff01' or uchar == u'\u3001' or uchar == u'\uff0c':
        return True
    else:
        return False

# add new string to the super_dict:
def add_new_word(root, line, pos, accu):
    if pos == len(line) -1:
        root.accumulate = pos
        # print(root.accumulate)
        return
    if root.dict.get(line[pos], 0) == 0:
        root.dict[line[pos]] = super_dict()
    if root.dict[line[pos]].accumulate != 0:
        accu = root.dict[line[pos]].accumulate
    add_new_word(root.dict[line[pos]], line, pos+1, accu)
    return

# look up the super_dict to cut the sentence
def cut_sentence(sentence, root, start, offset, accu):
    if start+offset >= len(sentence):
        if root.accumulate :
            return root.accumulate
        else:
            return accu
    if is_alphabet(sentence[start]):
        tmp = 0
        while is_alphabet(sentence[start+tmp]):
            tmp += 1
            if start+tmp == len(sentence):
                break
        return tmp
    if root.accumulate != 0:
        accu = root.accumulate
#    print(root.dict.get(sentence[start+offset], 0), sentence[start+offset], accu, root.accumulate)
    if root.dict.get(sentence[start+offset], 0) == 0 :
        if is_punc(sentence[start]):
            return 1
        if accu:
            return accu
        else:
            return 1
    return cut_sentence(sentence, root.dict[sentence[start+offset]], start, offset+1, accu)

def WS(sentence):

        #sentence = input()
        sentence_length = len(sentence)


        root = super_dict()
        # dic_no_space.txt need to place in the same directroy with this program
        f = open('./WS/dict_no_space.txt', encoding="utf-8-sig")
        line = f.readline()

        while line:
            add_new_word(root, line, 0, 0)
            line = f.readline()

        i = 0
        result = []
        late = 0
        while i < sentence_length:
            late = cut_sentence(sentence, root, i, 0, 0)
            result.append(sentence[i:i+late])
            i += late
        re = []
        for k in result:
            if len(k) != 1 or ( k >= '0' and k <= '9' ):
                re.append(k)
        return re

if __name__ == "__main__":
    print(WS("123"))
