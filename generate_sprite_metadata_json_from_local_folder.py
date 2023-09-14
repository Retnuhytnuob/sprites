import os
import json
import re

# Define the constant pCount with a default value of 450
pCount = 0

directory = './CustomBattlers'
output_file = 'custom_sprite_metadata.json'

def count_files(directory):
    result = {}
    
    #prepopulate with all current pokemon indexes
    for h in range(1, pCount + 1):
        result[h] = {}
        for b in range(1, pCount + 1):
            result[h][b] = {'m': 0, 'a': 0} 

    # Regular expression pattern for matching the filename
    pattern = re.compile(r'(\d+)\.(\d+)([a-zA-Z]*)\.png')

    # Iterate through files in the directory
    for filename in os.listdir(directory):
        # Use regular expression to extract parts of the filename
        match = pattern.match(filename)
        if match:
            h, b, letter = match.groups()

            # Convert h and b to integers
            try:
                h = int(h)
                b = int(b)
            except ValueError:
                continue

            # Add a record if not already existing
            if h not in result:
                result[h] = {}
            if b not in result[h]:
                result[h][b] = {'m': 0, 'a': 0}

            # Update 'a' count for files with letter parts, 'm' if a main sprite exists
            if letter:
                result[h][b]['a'] += 1
            else: 
                result[h][b]['m'] = 1

    return result


result = count_files(directory)

# Sort the results by converting keys to integers and then sorting
sorted_result = {int(h): {int(b): values for b, values in inner.items()} for h, inner in result.items()}


with open(output_file, 'w') as json_file:
    json.dump(sorted_result, json_file, indent=2, sort_keys=True)

print(f'Sorted result exported to {output_file}')
