#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from nltk.tokenize import sent_tokenize, word_tokenize
import nltk
from os.path import isfile, join
from pathlib import Path
import sys
import glob
import os
import re

dictionary = pd.read_json(sys.argv[0], lines=True)
subs = pd.read_excel(sys.argv[1])
output = sys.argv[2]
dictionary['word'] = dictionary['word'].str.lower()

def get_words(subtitles):
    # Deletes brackets that contain the speaking character's name and removes leading white space.
    sents = [sent_tokenize(re.sub(r'\[[^()]*\]', '', subtitle).lstrip()) for subtitle in subtitles]
    # Makes first letter of sentences lower case so they can be matched to their dictionary definitions.
    for index, sub in enumerate(sents):
        sents[index] = sub[0].replace(sub[0], sub[0].lower(), 1)
    
    # Get all words from each sentence.
    parsed = [word_tokenize(re.sub(r'[^\w\s]', '', sent)) for sent in sents]
    # Flatten list to 1 dimensional.
    words = [word for item in parsed for word in item]
    
    return list(set(words))


def get_def(word, template):
    # 'head', for the most part, indicates it is an alternate form of the word.
    if template == 'head':
        try:
            # Alternate forms of verbs have the quality 'form_of'
            to_find = dictionary.loc[dictionary['word'] == word]['senses'].iloc[0][0]['form_of'][0]['word']
            to_find = to_find.lower()
            definition = dictionary.loc[dictionary['word'] == to_find]['senses'].iloc[0][0]['glosses'][0]
            return to_find, definition
            
        except:
            # Alternate forms of nouns have the quality 'alt_of'
            to_find = dictionary.loc[dictionary['word'] == word]['senses'].iloc[0][0]['alt_of'][0]['word']
            to_find = to_find.lower()
            definition = dictionary.loc[dictionary['word'] == to_find]['senses'].iloc[0][0]['glosses'][0]
            return to_find, definition

    else:
        definition = dictionary.loc[dictionary['word'] == word]['senses'].iloc[0][0]['glosses'][0]
        return word, definition
    
    
def get_gender(word):
    gender = dictionary.loc[dictionary['word'] == word].iloc[0]['head_templates'][0]['args']['1'][0]
    
    if gender == 'm':
        return 'der'
    elif gender == 'n':
        return 'das'
    else:
        return 'die'
    
    
dictionary['word'] = dictionary['word'].str.lower()
words = get_words(subs['Subtitle'])
words_meanings = []
for idx, word in enumerate(words):
    # If the word is not in the dictionary, then skip to the next word.
    if len(dictionary.loc[dictionary['word'] == word]['senses']) == 0:
        continue
            
    try:
        word_temp = dictionary.loc[dictionary['word'] == word]['head_templates'].iloc[0][0]['name']
    except TypeError:
        std_form, definition = get_def(word, None)
        words_meanings.append({'word': std_form, 'definition': definition})
        continue
        
    try:
        std_form, definition = get_def(word, word_temp)
    except:
        std_form, definition = word, dictionary.loc[dictionary['word'] == word]['senses'].iloc[0][0]['glosses'][0]
        
    if word_temp == 'de-noun':
        words_meanings.append({'word': get_gender(std_form) + ' ' + std_form[0].replace(
            std_form[0], std_form[0].upper(), 1) + std_form[1:], 'definition': definition})
    else:
        words_meanings.append({'word': std_form, 'definition': definition})
            
    cards = pd.DataFrame(words_meanings)

cards.to_csv(output)