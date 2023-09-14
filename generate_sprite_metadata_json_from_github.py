import os
import json
import re
import time
# requires the requests package. pip install requests
import requests

# pCount value will pre-populate the json with all pokemon numbers, for both head/body
# 0 causes the result json to only have entries if there is a custom sprite for the head/body pair.
pCount = 0

#Github repo information. Change this if the repo moves
repo_image_folder_path = f'https://api.github.com/repos/infinitefusion/sprites/contents/CustomBattlers'

# Name of file to export the result into as a JSON file
output_file = 'custom_sprite_metadata.json'

# GitHub API rate limiting variables
github_token = ''  # Leave empty for unauthenticated rate limiting, or replace with your GitHub token
github_api_base_url = 'https://api.github.com'

# Function to check and wait for rate limits
def check_rate_limit():
    if github_token:
        response = requests.get(f'{github_api_base_url}/rate_limit', headers={'Authorization': f'token {github_token}'})
        print(f"{response}")
    else:
        response = requests.get(f'{github_api_base_url}/rate_limit')

    rate_limit_data = response.json()

    if github_token:
        core_limit = rate_limit_data['resources']['core']
        remaining_requests = core_limit['remaining']
    else:
        remaining_requests = rate_limit_data['rate']['remaining']

    if remaining_requests <= 0:
        if github_token:
            reset_time = core_limit['reset']
        else:
            reset_time = rate_limit_data['rate']['reset']

        sleep_time = reset_time - int(time.time()) + 5  # Wait a few seconds after reset
        print(f"Rate limit exceeded. Waiting for {sleep_time} seconds...")
        time.sleep(sleep_time)

def fetch_sprite_list_to_data_arrays():
    result = {}
    
    #prepopulate with all current pokemon indexes
    for h in range(1, pCount + 1):
        result[h] = {}
        for b in range(1, pCount + 1):
            result[h][b] = {'m': 0, 'a': 0}    
    
    try:
        page = 1
        per_page = 2000  # Number of items per page, adjust as needed
        
        while True:
            check_rate_limit()  # Check rate limit before making each request

            # Make an API request to fetch the contents of the "CustomBattlers" folder
            params = {'page': page, 'per_page': per_page}
            response = requests.get(repo_image_folder_path, params=params)
            response.raise_for_status()

            # Parse the JSON response
            repo_contents = response.json()
            
            # If the response is empty, we have fetched all files
            if not repo_contents:
                break
                
            # Regular expression pattern for matching the filename
            pattern = re.compile(r'(\d+)\.(\d+)([a-zA-Z]*)\.png')

            for file_info in repo_contents:
                # Extract the file name from the API response
                filename = file_info['name']
                
                # Use regular expression to extract parts of the filename
                match = pattern.match(filename)
                if match:
                    # Head, Body, alternate variant
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
                        
            # Move to the next page
            page += 1
    except requests.exceptions.RequestException as e:
        print(f"Error fetching files from GitHub: {str(e)}")
        
    return result

result = fetch_sprite_list_to_data_arrays()

# Sort the results by converting keys to integers and then sorting
sorted_result = {int(h): {int(b): values for b, values in inner.items()} for h, inner in result.items()}

with open(output_file, 'w') as json_file:
    json.dump(sorted_result, json_file, indent=2, sort_keys=True)

print(f'Result exported to {output_file}')
