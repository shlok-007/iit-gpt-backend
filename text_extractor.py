# python code to extract text from various types files or images in a directory and save them in another directory

import os
import textract
from tqdm import tqdm

def extract_text_from_file(file_path):
    """Extract text from a file."""
    return textract.process(file_path).decode('utf-8')

directory = 'ARP'

# Create a new directory to store the extracted text
if not os.path.exists('text_data'):
    os.makedirs('text_data')

# check for all files in the directory recursively

for root, dirs, files in tqdm(os.walk(directory)):
    for file in files:
        file_path = os.path.join(root, file)
        # check if the file has an extension
        if('.' not in file_path or file_path.split('.')[-1] == ''):
            continue
        try:
            text = extract_text_from_file(file_path)
            # Save the extracted text to a new file
            with open(f'text_data/{file}.txt', 'w') as f:
                f.write(text)
            # print(f'Extracted text from {file_path} and saved to text_data/{file}')
        except Exception as e:
            print(f'Error extracting text from {file_path}: {e}')