import re
import os
from docx import Document

# Directory containing the .docx files
directory = '/Users/admin1/Desktop/cv'
env_file = '.env'

# Function to clean text
def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

# Function to read .docx file and return its text
def read_docx(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

# Iterate through all .docx files in the directory
for file_name in os.listdir(directory):
    if file_name.endswith('.docx') and not file_name.startswith('~$'):
        file_path = os.path.join(directory, file_name)
        try:
            text = read_docx(file_path)
            cleaned_text = clean_text(text)
            
            # Extract the base name without the extension for the env variable name
            base_name = os.path.splitext(file_name)[0]
            
            # Write the clean text to .env file
            with open(env_file, 'a') as file:
                file.write(f'{base_name}="""{cleaned_text}"""\n')
        except Exception as e:
            print(f"Skipping file {file_name} due to error: {e}")

print("CVs have been parsed and added to the .env file.")
