# Haiku generation logic

from estnltk import Text
from estnltk.taggers.morph_analysis.proxy import MorphAnalyzedToken
from estnltk.vabamorf.morf import syllabify_words

from nltk import ConditionalProbDist, ConditionalFreqDist, MLEProbDist

import time
from pickle import load, dump
from itertools import chain
from random import choice, seed
from collections import Counter, defaultdict
from os import listdir
from os.path import isfile
from re import compile, split

ROWS = [5, 7, 5]
random_inspirations = ['talu', 'mees', 'perenaine', 'kala', 'mets', 'hobune', 'aeg', 'leib', 'linn', 'kool', 'maja', 'laps']
word_replacements = ['ja', 'et', 'kui', 'või', 'on', 'nii', 'ent',
                     'aga', 'tema', 'meie', 'ilma', 'mõtleks'] # must contain a 1-syllable word
ngram_sizes = [7, 6, 5, 4, 3, 2] # unique ngram sizes (>=2) in use order, must end with 2
sets_path = "cache/sets.p"
subsets_path = "cache/subsets.p"

def start_time():
    return time.time()

def stop_time(start, name):

    delta = time.time() - start
    print(name + ': ' + str(round(delta, 2)) + 's')

#seed(123)

class Haikusaare:

    def __init__(self, corpus_path='corpus/'):
        start = start_time()
        generate_subsets = True

        if isfile(sets_path):
            print('Sets file found, loading sets from cache.')
            self.sets_of_ngrams = load(open(sets_path, 'rb'), encoding='utf-8')

            if isfile(subsets_path):
                print('Subsets file found, loading subsets from cache.')
                generate_subsets = False
                self.subsets_of_ngrams = load(open(subsets_path, 'rb'), encoding='utf-8')
        else:
            print('Sets file not found, generating sets from corpus')
            self.sets_of_ngrams = get_ngrams_from_corpus(corpus_path)
            dump(self.sets_of_ngrams, open(sets_path, 'wb'))

        if generate_subsets:
            print('Subsets or sets file not found, generating subsets from cache.')
            self.subsets_of_ngrams = get_ngrams_subsets(self.sets_of_ngrams)
            dump(self.subsets_of_ngrams, open(subsets_path, 'wb'))

        stop_time(start, 'mudel')

    def generate_haiku(self, insp):
        start = start_time()
        response = generate_haiku(self.subsets_of_ngrams, insp)
        stop_time(start, 'haiku')
        return response

# init

def get_ngrams_from_corpus(corpus_path):

    filenames = get_filenames(corpus_path)
    filecount = len(filenames)

    sets_of_ngrams = [[] for _ in ngram_sizes]

    for file_index in range(filecount):

        filename = filenames[file_index]
        print('Loen faili ' + filename + '... (' + str(file_index+1) + '/' + str(filecount) + ')')
        filepath = corpus_path + filename

        file = open(filepath, encoding='utf-8')
        text = file.read()#.lower()
        file.close()
        
        sentences = process_text(text)
        sentences = truecase_sentences(sentences)

        for ngram_index in range(len(ngram_sizes)):
            ngram_size = ngram_sizes[ngram_index]
            #print('building ' + str(ngram_size) + '-grams from ' + str(ngram_sizes) + 'grams')

            for sentence in sentences:
                for k in range(ngram_size - 1, len(sentence)):
                    ngram = []

                    for l in range(k + 1 - ngram_size, k + 1):
                        ngram.append(sentence[l])

                    sets_of_ngrams[ngram_index].append(ngram)

    return sets_of_ngrams

def get_filenames(corpus_path):

    entitynames = listdir(corpus_path)
    filenames = []

    for entityname in entitynames:
        if isfile(corpus_path + entityname):
            filenames.append(entityname)

    return filenames

# text -> List of lists of words
# EstNLTK word tokenization is slower and not perfect with our variety of quote marks so we use our own
def process_text(text):

    # nearly all occurrences of w are wrong, there are very few names and very little German
    text = text.replace('W', 'V').replace('w', 'v')

    sentence_strings = split(r'[.!?]|\n\n', text)

    ignore_chars = compile(r'’\'•~') # ä'ä, see'p, vaat' or trash characters
    sure_splitting_chars = compile(r'[,;:«»"„”ˮ“‚‘*/\\()\[\]\n\t…]|\.\.\.') # characters that always split a word
    maybe_splitting_chars = compile(r'[\-–—_]+[ $]') # characters that sometimes split a word

    sentences = []
    for sentence_string in sentence_strings:

        # anomalies that got through:
        # multiple punctuations, "word-", "word-,", "-,", ",-"

        #estnltk_text = Text(sentence_string)
        #estnltk_text.tag_layer(['words'])
        #textwords = estnltk_text.words.text

        sentence = ignore_chars.sub('', sentence_string)
        sentence = sure_splitting_chars.sub(' ', sentence)
        sentence = maybe_splitting_chars.sub(' ', sentence)

        #if len([word for word in sentence.split(' ') if len(word) == 1]) > 0: # explore corpus
        #    print([word for word in sentence.split(' ') if len(word) == 1], end='')

        sentence = [word for word in sentence.split(' ') if len(word) > 1]

        #if len(sentence) == 1: # explore corpus
        #    print(sentence, end='')

        if len(sentence) > 1:
            sentences.append(sentence)

    return sentences

def truecase_sentences(sentences):

    labelled = []
    for sentence in sentences:
        for i, word in enumerate(sentence):
            if i > 0:
                labelled.append((word.lower(), word))

    model = ConditionalProbDist(ConditionalFreqDist(labelled), MLEProbDist)

    result = []
    for sentence in sentences:
        #for i, word in enumerate(sentence):
        #    try:
        #        sentence[i] = model[word.lower()].max()
        #    except ValueError:
        #        sentence[i] = word.lower()

        try:
            sentence[0] = model[sentence[0].lower()].max()
        except ValueError:
            sentence[0] = sentence[0].lower()

        result.append(sentence)

    return result

# Indexes ngrams in a set of ngrams by first letter of last prefix word
def get_ngrams_subsets(sets_of_ngrams):

    subsets = dict()
    for ngrams in sets_of_ngrams:
        ngram_subsets = defaultdict(list)

        for ngram in ngrams:
            #first letter of last prefix word
            letter = ngram[len(ngram)-2][0]
            ngram_subsets[letter].append(ngram)

        subsets[len(ngrams[0])] = ngram_subsets

    return subsets

# generation

def generate_haiku(subsets_of_ngrams, insp):

    if len(insp) > 200:
        insp = ''

    insp = insp.strip().lower()
    insp_word = valid_word_from_string(insp)

    previous_words = [get_random_inspiration()]
    if insp_word is not None:
        previous_words = [insp_word]
    last_used_gram_size = 1

    answer = ''
    for row_length in ROWS:

        syllables_left = row_length
        if len(answer) != 0:
            answer += '\n'

        while syllables_left > 0:
            default_word_given = False

            word, last_used_gram_size = get_next_word(subsets_of_ngrams, previous_words, syllables_left, last_used_gram_size)

            # if no word of sufficient length found
            if word is None:
                word = get_word_replacement(syllables_left)
                last_used_gram_size = 1
                default_word_given = True

            syllable_length = len(syllabify_string(word))

            answer += word

            # TODO: remove for production
            #if default_word_given:
            #    answer += '!'
            #else:
            #    answer += str(last_used_gram_size-1)

            previous_words.append(word)

            syllables_left -= syllable_length
            if syllables_left > 0:
                answer += ' '

    return answer


def get_next_word(subsets_of_ngrams, previous_words, syllables_left, last_used_gram_size):

    return_candidate = None
    return_candidate_n = None

    # first letter of last previous word
    letter = previous_words[-1][0]
    #bigram_subsets = subsets_of_ngrams[2]
    
    for ngram_size in ngram_sizes:

        # If the last best choice was made with (ngram_size)grams, the next can't be made with bigger than (ngram_size+1)grams
        if ngram_size > last_used_gram_size + 1:
            continue

        potential_matches = subsets_of_ngrams[ngram_size][letter]
        matches = get_matches(potential_matches, previous_words, syllables_left)

        filtered_matches = matches
        # TODO: only heavily needed if many ! words come up, but worth if can be done up front
        #filtered_matches = [match for match in matches if word_is_good(match, bigram_subsets[match[0]], syllables_left)]

        if len(filtered_matches) != 0:
            return choice(filtered_matches), ngram_size # TODO: make it more popularity based?
        elif len(matches) != 0 and return_candidate is None:
            return_candidate = choice(matches)
            return_candidate_n = ngram_size

    if return_candidate is not None:
        return return_candidate, return_candidate_n
    return None, None

#possible to optimize by looking at 2 characters
def get_matches(ngrams, previous_words, syllables_left):
    ngram_size = len(ngrams[0])  # gram size
    n = ngram_size - 1  # number of previous words to look at, also index of predicted word in ngram

    if len(previous_words) >= n:
        recent_words = previous_words[-n:]
        return [ngram[n] for ngram in ngrams
                if recent_words == ngram[:n]
                and len(syllabify_string(ngram[n])) <= syllables_left]

    else:
        p = len(previous_words)
        return [ngram[n] for ngram in ngrams
                if previous_words == ngram[n - p:n]
                and len(syllabify_string(ngram[n])) <= syllables_left]

"""
# TODO: rebuild
# todo: rename
def word_is_good(match, filtered_bigrams, syllables_left):
    future_syllables = syllables_left - len(syllabify_string(match))

    # word does not need to be continuable if it ends the line
    return future_syllables == 0 or word_is_continuable(filtered_bigrams, match, future_syllables)

# one layer of checking, more possible
# todo: extremely inefficient, startupil ette arvutada iga bigrami teiste sõnade hulga kohta? (6+ min estimated)
def word_is_continuable(filtered_bigrams, word, syllables_left):
    for bigram in filtered_bigrams:
        if bigram[0] == word and len(syllabify_string(bigram[1])) <= syllables_left:
            return True
    return False
"""

def valid_word_from_string(sentence):

    text = Text(sentence)
    text.analyse('morphology')
    morph = text.morph_analysis

    words = []

    for line in morph:
        #word = line[0].lemma
        word = sentence.lower().split(' ')[0]

        if MorphAnalyzedToken(word).is_word or len(line.root_tokens) > 1:
            # is valid word or has valid word as part of it
            # some words and names will be lost here
            return word

    return None


def get_random_inspiration():
    return choice(random_inspirations)

def get_word_replacement(syllables_left):
    result = choice(word_replacements)

    while syllables_left < len(syllabify_string(result)):
        result = choice(word_replacements)

    return result

def syllabify_string(string, as_dict=False):
    #print('syllabifying "' + string + '" - ', end='')
    word_syllables = syllabify_words(string.lower().split(' '), as_dict)
    all_syllables = list(chain.from_iterable(word_syllables))
    #print(' - done!')
    return all_syllables

def sorted_wordcount(arr):
    return sorted(unsorted_wordcount(arr), key=lambda kv: kv[1], reverse = True)

def unsorted_wordcount(arr):
    return Counter(arr).items()
