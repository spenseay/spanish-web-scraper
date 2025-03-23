import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import json
import os
import csv

import pandas as pd

"""
Reads a csv file containing spanish words formatted with one word per row and every word in column 1
Args: file_path (str): the path to the csv file
Returns: pd.Dataframe a pandas dataframe containing the Spanish words
"""
def load_spanish_words(file_path):
    df = pd.read_csv(file_path, header=None)
    
    # names first column
    df.columns = ['Spanish Word']    
    return df

"""
Reads a word parses a website for sentences containing that word
Args: word - a word to find sentences using that word
Returns: a touple of a sentence using that word one in english and one in spanish
"""

def fetch_sentences(word):
    try:
        url = f"https://www.online-translator.com/contexts/spanish-english/{word}"
        print(f"Fetching example for word: {word}")
        print(f"URL: {url}")

        response = requests.get(url)

        # error check
        if response.status_code != 200:
            print(f"Failed to fetch examples for '{word}'. Status code: {response.status_code}")
            return None, None
        html = BeautifulSoup(response.text, 'html.parser')
        sentence_pair = html.find('div', class_= 'samplesList')

        spanish_span = sentence_pair.find('span', class_= 'samSource')
        spanish_sentence = spanish_span.get_text(strip=False) if spanish_span else None
        
        english_span = sentence_pair.find('span', class_= 'samTranslation')
        english_sentence = english_span.get_text(strip=False) if english_span else None

        return spanish_sentence, english_sentence

    except Exception as e:
        print(f"Error fetching example for {word}': {e}")
        return None, None
    
def test_fetch():
    word = 'familia'
    
    # Fetch an example for the word
    spanish_sentence, english_sentence = fetch_sentences(word)
    
    # Display the results
    print("\nResults:")
    print(f"Word: {word}")
    print(f"Spanish Sentence: {spanish_sentence}")
    print(f"English Translation: {english_sentence}")


# testing to see if load_spanish_words works
if __name__ == '__main__':
 
    # Your existing code to load and display words
    words_df = load_spanish_words('top_2000_spanish_words.csv')
    
    print("\nDataFrame Info:")
    print(words_df.info())
    
    print("\nFirst 10 words:")
    print(words_df.head(10))
    
    # Now test the sentence fetching
    print("\nTesting sentence fetching for 'familia':")
    test_fetch()