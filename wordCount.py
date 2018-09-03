'''
    Name: Fernando Martinez
    Class: CS 4375 OS
'''

import sys                                  # Command line arguments.

if len(sys.argv) is not 3:                  # Check the correct amount of arguments.
    print("Correct usage: wordCount.py <input text file> <output text file>")
    exit()

inFile = sys.argv[1]                    # Read the argument for the input file.
outFile = sys.argv[2]                   # Read the argument for the output file.
inFile = open(inFile)                   # The input file
wordCount = {}                          # The dictionary for the counter of the words.


def addWord(word):                      # Add the word to the dictionary.
    if word not in wordCount:           # If word not in the dictionary add it and start the counter at 1.
        wordCount[word] = 1
    else:                               # Else add 1 to the counter.
        wordCount[word] += 1


def stripWord(word):
    return word.strip(".").strip(":").strip(",").strip(";").strip("\"").strip(".\"").lower()


for word in inFile.read().split():      # Loop the file and split it at every space.
    word = stripWord(word)              # Trim the word from the punctuation symbols.
    if '-' in word:                     # If the word contains '-' split it.
        tmpWord = word.split('-')
        for tmp in tmpWord:             # Loop to add the new splitted words.
            tmp = stripWord(tmp)
            addWord(tmp)
    elif '\'' in word:
        tmpWord = word.split('\'')
        for tmp in tmpWord:             # Loop to add the new splitted words.
            tmp = stripWord(tmp)
            addWord(tmp)
    else:
        addWord(word)

outFile = open(outFile, "w")            # Open the file for the output.

for word in sorted(wordCount):          # Loop to write the dictionary to the output file.
    if word == "":
        continue
    outFile.write("{} {}\n".format(word, wordCount[word]))

# Close the files.
inFile.close()
outFile.close()
