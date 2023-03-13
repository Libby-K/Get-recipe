#!/bin/bash

# Prompt the user to enter a URL
echo "Enter a URL:"
read url
echo "URL entered: $url"

# Call the my_function() function with the URL input and store the result in a variable
result=$(python3 scrape_data_.py "create_json" "$url")
echo "Result: $result"

# Print the result to a file
echo "$result" > output.txt
echo "Output saved to output.txt"

# Pause the script and wait for user input
echo "Press Enter to exit"
read