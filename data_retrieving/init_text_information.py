#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# The goal of this program is to retrieve text information. 
# Ulitmately the content of the text, amendments and so on 
# For now only the url to the text

# To do: Retrieve and parse data from text

# File management package
import os

# Json data management
import json

# Retrieve website
import requests as rq

# Parsing package (for the future)
from bs4 import BeautifulSoup as bs

def already_considered_ref(src_file):
    """Retrieved all parsed reference

    Args:
        src_file (str): Pathfile to the file that stores data

    Returns:
        List: List of text references
    """
    already_considered = []
    if os.path.isfile(src_file):
        with open(src_file, "r") as read_file:
            already_considered = [cur_line.split(",")[0] for cur_line in  read_file.readlines()]
    return already_considered


def gen_src_list(already_considered, src_dir="tmp/stage_1/"):
    """Generator of text references to parse these data

    Args:
        already_considered (List): List of text references
        src_dir (str, optional): Source file to retrieve data. Defaults to "tmp/stage_1/".

    Yields:
        str: Reference of the voted text
    """
    file_list = [cur_file for cur_file in os.listdir(src_dir) if "Vote_" in cur_file]
    for cur_file in file_list:
        votes_data = None 
        with open(src_dir + cur_file, "r") as vote_json:
            votes_data = json.load(vote_json)
        
        for vote in votes_data["data"]:
            text_ref = vote["reference"]
            if text_ref is not None:
                if text_ref not in already_considered:
                    already_considered.append(text_ref)
                    yield text_ref


def retrieve_text_name(text_url):
    parsed_website = bs(rq.get(text_url).content, "html.parser")
    main_text_title = parsed_website.findAll(attrs={"class": "erpl_title-h1"})[0].text
    return main_text_title


def write_text_data(texts_info, filepath):
    """Write retrieved data

    Args:
        texts_info (List[Vect]): List of data retrieved (reference, url)
        filepath (str): filepath to the target
    """
    texts_str_data = ""

    for text_info in texts_info:
        texts_str_data += ",".join(text_info) + "\n"

    with open(filepath, "a") as write_file:
        write_file.write(texts_str_data)


if __name__ == "__main__":
    url_template = "https://www.europarl.europa.eu/doceo/document/{}_EN.html"
    write_pathfile = "tmp/stage_1/text_info.csv"
    all_data = []
    already_considered = already_considered_ref(write_pathfile)
    for text_ref in gen_src_list(already_considered):
        text_url = url_template.format(text_ref)
        text_name = retrieve_text_name(text_url)
        all_data.append((text_ref, text_name, text_url))
    write_text_data(all_data, write_pathfile)


