import sys
import re

# Extract the file name as a parameter
file_name = sys.argv[1]
cv = sys.argv[2]

# Run the file
with open(file_name, 'r') as file:
    text = file.read()

# Clean the text
clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

# Write the clean text to .env file
env_file = '.env'
with open(env_file, 'a') as file:
    file.write(f'{cv}="""{clean_text}"""\n')
