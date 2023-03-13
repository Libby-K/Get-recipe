
# Imports

from tensorflow import keras
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
from bs4 import BeautifulSoup
import requests
import re
import json

# Define params
TOKENIZER_PATH = 'recipe_tokenizer.json'
MODEL_PATH = 'classifier'
MAX_LENGTH = 1000


FILE_PATH = 'dataset.tsv'



# function to extract the body content of a webpage given its URL
def extract_url_body(url):
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    return soup.find('body')

# function to extract instruction and ingredient divs from a webpage given its URL
def extract_instructions_ingredient_divs(url):

    # extract the body content of the webpage
    body = extract_url_body(url)

    # initialize an empty list to store the scraped divs
    scraped_list = []

    # list of keywords to identify divs containing instructions or ingredients
    lookup = ['Instructions', 'Directions', 'Guidelines', 'Preparation', 'Cooking process', 'Steps',
              'Ingredients', 'Components', 'Materials', 'Constituents']

    # join the lookup keywords with '|' for use in a regex pattern
    tokens = '|'.join(token for token in lookup)

    # regex pattern to ignore divs containing dates and certain irrelevant keywords
    ignore_pattern = re.compile(r"\d{2}\.\d{2}\.\d{4}(?!.*(?:love|like|tried|best ))", re.IGNORECASE)

    # find all divs in the webpage body
    divs = body.find_all('div')

    # loop over all the divs
    for div in divs:
        # get the text content of the div and strip any whitespace
        div_text = div.text.strip()
        # check if the div contains any of the lookup keywords and does not contain any dates or irrelevant keywords
        if (re.findall(tokens, div_text, flags=re.IGNORECASE)) and (not re.search(ignore_pattern, div_text)):
            # if the conditions are met, append the div text to the scraped_list
            scraped_list.append(div_text)

    # filter out divs with length less than or equal to 200 characters
    long_scraped_list = [s for s in scraped_list if len(s) > 200]
    
    return long_scraped_list

def split_clean_scraped_list(scraped_list):
    
    # Define a list of words to split the scraped text on, and add a newline character for splitting 
    # paragraphs or sections
    split_words = ['Instructions', 'Directions', 'Guidelines', 'Preparation', 'Cooking process', 'Steps',
              'Ingredients', 'Components', 'Materials', 'Constituents','\n']
    result = []
    
    # Split each item in scraped_list using the split_words as delimiters
    for item in scraped_list:
        parts = [item]
        for word in split_words:
            # Make a copy of the list to iterate over to avoid modifying the list during iteration
            parts_copy = parts.copy()
            parts = []
            for part in parts_copy:
                # Split on the word, remove leading/trailing spaces, and append to the parts list
                parts.extend([s.strip() for s in re.split(f"(?i){word}", part)])
        # Append the split parts to the result list
        result.extend(parts)

    # Remove empty strings from result, duplicates, and items containing question marks
    result = list(filter(bool, result))
    result = list(set(result))
    result = [item for item in result if '?' not in item]
    
    # Filter the result list to include only items with length greater than 200 characters
    result = [s for s in result if len(s)>200]
    
    # Return the cleaned and filtered result list
    return result

def load_tokenizer(tokenizer_path = TOKENIZER_PATH):
    # Load the tokenizer from the specified path.
    with open(tokenizer_path , 'r') as tokenizer_file:
        # Convert the JSON string to a tokenizer object.
        return tf.keras.preprocessing.text.tokenizer_from_json(tokenizer_file.read())

def preprocess_text(data):
    # Load the tokenizer.
    tokenizer = load_tokenizer()
    # Convert the data to sequences using the tokenizer.
    sequences = tokenizer.texts_to_sequences(data)
    # Pad the sequences to ensure they all have the same length.
    padded = pad_sequences(sequences, maxlen=MAX_LENGTH)
    # Return the padded sequences as a numpy array.
    return np.array(padded)

def load_model(model_path = MODEL_PATH):
    # Load the trained model from the specified path.
    model = keras.models.load_model(model_path)
    # Return the loaded model object.
    return model

def create_json(url):
    # Initialize empty lists to store ingredients and instructions
    ingredients = []
    instructions = []
    
    # Load the trained model for text classification
    model = load_model()
    
    # Extract the divs containing instructions and ingredients from the web page
    scraped_list = extract_instructions_ingredient_divs(url)
    
    # Split and clean the scraped text into individual parts
    clean_scraped_list = split_clean_scraped_list(scraped_list)
    
    # Loop through each part in the cleaned list
    for p in clean_scraped_list:
        # Preprocess the text by tokenizing and padding it for input to the model
        processed_text = preprocess_text(p)
        
        # Use the model to make a prediction on the processed text and calculate the mean of the predictions
        prediction = model.predict(processed_text)
        mean_arr = np.mean(prediction, axis=0)
        print(mean_arr)

        # If the prediction for the first class (instruction) is higher than the threshold, add it to the instructions list
        if mean_arr[0] >=0.75:
            instructions.append(p)
        
        # If the prediction for the second class (ingredient) is higher than the threshold, add it to the ingredients list
        if mean_arr[1] >=0.75:
            ingredients.append(p)


    
    # Create a dictionary to store the ingredients and instructions lists
    recipe_dict = {
        'ingredients': ingredients,
        'instructions': instructions }

    # Extract the recipe name from the url and use it to construct a filename for the JSON file
    path = url.split('.com')[1][1:-1] + '_recipe.json'
    
    # Write the recipe dictionary to a JSON file
    with open(path, 'w') as fp:
        json.dump(recipe_dict, fp)
    
    # Return the recipe dictionary
    return recipe_dict

if __name__ == '__main__':
    url = 'https://www.loveandlemons.com/vegan-meatballs/'
    recipe_dict = create_json(url)

