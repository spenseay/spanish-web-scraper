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
    df = pd.read_csv(file_path)
    return df

def fetch_definition(word):
    try:
        url = f"https://www.wordreference.com/definicion/{word}"
        print(f"Fetching definition for word: {word}")
        print(f"URL: {url}")

        response = requests.get(url)

        # error check
        if response.status_code != 200:
            print(f"Failed to fetch examples for '{word}'. Status code: {response.status_code}")
            return []
        
        html = BeautifulSoup(response.text, 'html.parser')
        first_definition = html.find('ol', class_="entry")
        first_definition = first_definition.find('li') if first_definition else None
        first_definition = first_definition.get_text(strip=False)
        first_definition = first_definition.split(':')[0] if first_definition else None  # Get the first line of the definition

        if not first_definition:
            print(f"No definition found for '{word}'.")
            return []

        return first_definition
    
    except Exception as e:
        print(f"Error fetching example for {word}': {e}")
        return []
    
print(fetch_definition('casa'))

def create_output_dataframe(input_file, output_file, delay):

    # set up dataframe and add column for definition
    data_frame = load_spanish_words('spanish_words_with_examples.csv')
    data_frame.insert(2, 'Spanish Definition', None )

    for index, row in data_frame.iterrows():
        word = row['Spanish Word']
        definition = fetch_definition(word)
        print(f"\nProcessing word {index+1}/{len(data_frame)}: {word}")

        data_frame.loc[index, 'Spanish Definition'] = definition

        # Save the results periodically
        if (index + 1) % 10 == 0 or index == len(data_frame) - 1:
            print(f"Saving progress: {index+1}/{len(data_frame)} words processed")
            data_frame.to_csv(output_file, index=False)

        time.sleep(delay)  # Delay to avoid overwhelming the server

    print(f"\nAll words processed. Saving final results to {output_file}")
    return data_frame

# main file to add definitions to csv
if __name__ == '__main__':
 
    input_file = 'spanish_words_with_examples.csv'
    output_file = 'final_spanish_csv.csv'

    results_df = create_output_dataframe(input_file, output_file, 0.1)

    print(f"\n All done!")