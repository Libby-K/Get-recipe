# Get-recipe
a A program that extracts ingredients and directions from a recipe webpage, and output a JSON containing them based on web scraping and text classification mpdel.
The program is trained on two datasets: the loaveandlemons_dataset and a dataset from Kaggle: https://www.kaggle.com/datasets/hugodarwood/epirecipes/code?select=full_format_recipes.json. Both datasets have ingredients and directions in a table.

### The files :
1. generate_data: combines the two training dataset and scrapes neither data from loaveandlemons site for the model training
2. model: generates tokenizer to preprocess the data, trains a model and saves it
3. scrape_data: defines a function create_json which extracts instructions and ingredients from a web page given its URL. It does so by first defining two helper functions: extract_url_body which extracts the body content of a webpage and extract_instructions_ingredient_divs which extracts divs containing instructions or ingredients. The create_json function then loads a pre-trained text classification model, preprocesses the extracted text into sequences, makes a prediction on the sequences using the loaded model, and appends the extracted text to either the instructions or ingredients list depending on which class the text was predicted to belong to with a confidence level above a certain threshold. The output is a JSON object containing the extracted ingredients and instructions. 
4. recipe sh file that runs the  

The model and the tokenizer used to preprocess the input are saved under the files directory, while the training files are saved in the data directory.

### Time Complexity
The program's time complexity is O(n):

* extract_url_body(): This function has a time complexity of O(1) as it just makes a request to a URL and extracts the HTML body using BeautifulSoup.
* extract_instructions_ingredient_divs(): This function has a time complexity of O(n), where n is the number of divs in the HTML body of the URL. This is because it loops over all the divs and applies several regex patterns to identify the ones that contain instructions or ingredients.
* split_clean_scraped_list(): This function has a time complexity of O(m * n), where m is the number of split words, and n is the number of parts obtained after splitting the scraped text. This is because it loops over all the split words and then over all the parts obtained after splitting the text using each split word.
* preprocess_text(): This function has a time complexity of O(m * n), where m is the length of the input data, and n is the length of the sequences after tokenization and padding. This is because it applies tokenization and padding to each element of the input data.
* create_json(): This function has a time complexity of O(m * n), where m is the number of parts in the cleaned scraped list, and n is the length of the sequences after tokenization and padding. This is because it applies preprocess_text() to each part and uses a trained model to make predictions on each preprocessed part.

### Space Complexity
The program's space complexity is O(n):

The program keeps the contents of the webpage at O(n).
The classifications for each of the webpage's paragraphs are also kept at O(n)
