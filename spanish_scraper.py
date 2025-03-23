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
    df.columns = ['Spanish Word', 'English Definition']
    return df

"""
Reads a word parses a website for sentences containing that word
Args: word - a word to find sentences using that word
Returns: a list of touples containing a sentence using that word one in english and one in spanish
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
            return []
        
        html = BeautifulSoup(response.text, 'html.parser')
        all_samples = html.find_all('div', class_= 'samplesList')



        if not all_samples:
            print(f"No sentence pairs found for '{word}'.")
            return []
        
        sentence_pairs = []

        for sample in all_samples:
            spanish_span = sample.find('span', class_= 'samSource')
            spanish_sentence = spanish_span.get_text(strip=False) if spanish_span else None
            
            english_span = sample.find('span', class_= 'samTranslation')
            english_sentence = english_span.get_text(strip=False) if english_span else None

            if spanish_sentence and english_sentence:
                sentence_pairs.append((spanish_sentence, english_sentence))

        return sentence_pairs

    except Exception as e:
        print(f"Error fetching example for {word}': {e}")
        return []
    
# test function to fetch sentences for a given word
def test_fetch():
    word = 'amor'  # Example word to test
    
    # Fetch an example for the word
    sentence_pairs = fetch_sentences(word)
    
    # Display the results
    print("\nResults:")
    print(f"Word: {word}")
    print(f"Found {len(sentence_pairs)} example sentences")
    
    # Display each sentence pair
    for i, (spanish, english) in enumerate(sentence_pairs, 1):
        print(f"\nExample {i}:")
        print(f"Spanish: {spanish}")
        print(f"English: {english}")

"""
Creates and outputs a dataframe which has a first column of spanish words, a second
column of english definitions, and a third column of tuples with example sentences using that word in both languages 
any subsequent columns are more example sentence tuples

Args: input_file (str): the path to the csv file containing the spanish words and their definitions
      output_file (str): the path to the output csv file to save the dataframe to
        max_examples (int): the maximum number of example sentences to fetch for each word
        delay (float): the time to wait between requests to avoid overwhelming the server (default is 0.1 seconds)
"""
def creates_output_dataframe(input_file, output_file, max_examples, delay):

    # setting up dataframe and labels
    words_df = load_spanish_words(input_file)
    columns = ['Spanish Word', 'English Definition']
    for i in range(1, max_examples + 1):
        columns.append(f'Example_{i}')

    # intializes empty dataframe with the correct columns
    results_df = pd.DataFrame(columns=columns)

    for index, row in words_df.iterrows():
        word = row['Spanish Word']
        definition = row['English Definition']

        print(f"\nProcessing word {index+1}/{len(words_df)}: {word}")

        #creates new row using dictionary for sentence pair
        new_row = {'Spanish Word': word, 'English Definition': definition}
        sentence_pairs = fetch_sentences(word)

        # unpacks tuples to create new columns for each example sentence
        for i, (spanish, english) in enumerate(sentence_pairs):
            if i < max_examples:  # Limit to max_examples
                new_row[f'Example_{i+1}'] = f"({spanish}, {english})"

        # add results to data frame
        results_df = pd.concat([results_df, pd.DataFrame([new_row])], ignore_index=True)

        # Save the results periodically
        if (index + 1) % 10 == 0 or index == len(words_df) - 1:
            print(f"Saving progress: {index+1}/{len(words_df)} words processed")
            results_df.to_csv(output_file, index=False)

        time.sleep(delay)  # Delay to avoid overwhelming the server

    print(f"\nAll words processed. Saving final results to {output_file}")
    return results_df

# testing to see if load_spanish_words works
if __name__ == '__main__':
 
    input_file = 'spanish words + english definitions.csv'
    output_file = 'spanish_words_with_examples.csv'

    results_df = creates_output_dataframe(input_file, output_file, 20, 0.1)

    print(f"\n All done!")

