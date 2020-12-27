import requests
from bs4 import BeautifulSoup
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6'}

# 1. Get links to tunes from sitemap URLs
def get_tune_links():
    sitemap_links = [
        "https://www.slippery-hill.com/sitemap.xml?page=1",
        "https://www.slippery-hill.com/sitemap.xml?page=2",
        "https://www.slippery-hill.com/sitemap.xml?page=3",
        "https://www.slippery-hill.com/sitemap.xml?page=4"
    ]

    all_tune_links= []

    # Loop through sitemap pages
    for sitemap_link in sitemap_links:
        page = requests.get(sitemap_link)
        
        # Make sure status is 200, parse XML, find all links
        try:
            page.raise_for_status()
            soup = BeautifulSoup(page.text, "html.parser")

            tune_links = soup.find_all('loc')

            for tune_link in tune_links:
                all_tune_links.append(tune_link.text)
        
        except Exception as err:
            print(err, sitemap_link)

        time.sleep(1)

    # Write all links to file
    with open("all_tune_links.txt", "w") as f:
        for tune_link in all_tune_links:
            f.write(f"{tune_link}\n")

# get_tune_links()


# ------------------------------------------


# 2. Go to each tune link page. Get all data.
def get_data_from_tune_links():

    # Open file, remove linebreak, append to list
    tune_links = []
    with open("all_tune_links.txt", "r") as f:
        for line in f:
            tune_links.append(line[:-1])

    # Loop through tune pages
    for tune_link in tune_links:
        page = requests.get(tune_link, headers=headers)

        try:
            page.raise_for_status()
        except Exception as err:
            with open("error_log.txt", "a") as f:
                f.write(f"{err} {tune_link}")
        
        soup = BeautifulSoup(page.text, "html.parser")

        # Create dictonary with CSS locations of keys
        css_selectors = {}
        css_selectors["tune_name"] = "soup.find('h1').find('span').text"
        css_selectors["artist"] = "soup.find(class_='field--name-field-r-source').find(class_='field__item').text"
        css_selectors["played_by"] = "soup.find(class_='field--name-field-r-played-by').find(class_='field__item').text"
        css_selectors["key"] = "soup.find(class_='field--name-field-r-key').find(class_='field__item').text"
        css_selectors["tuning"] = "soup.find(class_='field--name-field-r-tuning').find(class_='field__item').text"
        css_selectors["mp3_link"] = "'https://www.slippery-hill.com' + soup.find(class_='field--name-field-r-uploaded-file').find('audio').find('source')['src']"
        css_selectors["tune_URL"] = "tune_link"
        # css_selectors["year"] = "soup.find(class_='field--name-field-r-year').find(class_='field__item').text"
        # css_selectors["media_source"] = "soup.find(class_='field--name-field-r-media-source').find(class_='field__item').text"

        # Loop through and assign key/values. Pass if they don't exist
        tune_dict = {}
        for key in css_selectors:
            try:
                tune_dict[key] = eval(css_selectors[key])
            except:
                pass

        with open("all_tunes_data.txt", "a") as f:
            f.write(f"{tune_dict}\n")

        print(f"{tune_link} successful!")

        # Be nice
        time.sleep(5)

# get_data_from_tune_links()


# ------------------------------------------

# all_tunes_data used for evaluation and sanitization below

from all_tunes_data import *

# ------------------------------------------

#3. Fix Key and Tuning inconsistencies 

def find_keys(key_query, tune_list):
    lst = []

    for tune in tune_list:
        try:
            if tune[key_query] not in lst:
                lst.append(tune[key_query])
        except:
            pass

    for i in lst:
        print(i)
            
# find_keys('key', all_tunes_data)
# find_keys('tuning', all_tunes_data)


# ------------------------------------------


# 4. Remove duplicates. Use mp3_link

def remove_duplicates():
    temp = []
    tunes = []
    for tune in all_tunes_data:
        for key, val in tune.items():
            if key == "mp3_link" and val not in temp:
                temp.append(val)
                if tune not in tunes:
                    tunes.append(tune)
                    with open("all_tunes_data_no_duplicates.txt", "a") as f:
                        f.write(f"{tune}\n")

    print(len(temp))
    print(len(tunes))

# remove_duplicates()


# ------------------------------------------


#5. Evaluate if Artist and/or Played_By exist
from all_tunes_data_no_duplicates import *
import json

def artist_and_played_by(tune_list):
    tunes_json = {}

    for tune in tune_list:
        try:
            if 'played_by' not in tune and 'artist' in tune:
                tune['played_by'] = tune['artist']
                print(tune)
        except:
            pass

    tunes_json['tunes'] = tune_list

    with open("tunes_json.txt", "w") as f:
        json.dump(tunes_json, f, indent=4)

# artist_and_played_by(all_tunes_data_no_duplicates)



# 6. Manual data fixes:
    # Remove trailing and leading spaces in entries


# ------------------------------------------