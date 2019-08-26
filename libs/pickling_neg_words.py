import pickle

file = open ("neg_words.txt", "rt")

negs = set()
count = 1
for line in file:
    print (count, line[:-1], end=", ")
    negs.add (line[:-1])
    count += 1

pickle.dump (negs, open("neg_words.pickle", "wb"))
