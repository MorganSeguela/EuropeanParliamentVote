#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# The main goal of this program is to extract country, national and european political group

# json file management
import json

# file management
import os

# Retrieve today date and transform it in string value
from datetime import datetime


def parl_data_file():
    """Retrieve parliamentarian data file paths

    Yields:
        str: filepath to parliamentarians information
    """
    start_dir = "tmp/stage_1/"
    parl_files = [parl_file for parl_file in os.listdir(start_dir) if  "parliamentarian_main_info" in parl_file]
    for parl_file in parl_files:
        yield start_dir + parl_file


def parse_parl_file():
    """Open and parse json files

    Returns:
        dict: {parl_id:{fullname,country, politcalGroup, nationalPoliticalGroup}}
    """
    parl_data = {}
    for parl_file in parl_data_file():
        cur_data = {}
        with open(parl_file, "r") as json_parl:
            cur_data = json.load(json_parl)
        for cur_id in cur_data.keys():
            parl_data[cur_id] = cur_data[cur_id]
    return parl_data


def pg_created_file():
    """Retrieve data from political group data to get abbreviation

    Returns:
        List[List]: List of political group and their abbreviation
    """
    pg_file = "tmp/stage_1/created_political_group_data.csv"
    pg_data = []
    with open(pg_file, "r") as pg_file:
        pg_data = [pg_line.rstrip().split(",") for pg_line in pg_file.readlines()]
    return pg_data


def extract_country(parl_data):
    """Extract unique country and replace their index in the dictionary

    Args:
        parl_data (dict): parliamentarian information

    Returns:
        (dict, list): result of replacement and list of countries
    """
    country_found = []
    for one_parl in parl_data.keys():
        this_country = parl_data[one_parl]["country"]
        if this_country not in country_found:
            country_found.append(this_country)
        parl_data[one_parl]["country"] = country_found.index(this_country)
    return (parl_data, country_found)
            

def extract_npg(parl_data):
    """Extract national political group and replace it in dictionary

    Args:
        parl_data (dict): parliamentarian information

    Returns:
        (dict, list): result of replacement and list of national political groups
    """
    npg_found = []
    for one_parl in parl_data.keys():
        this_npg = parl_data[one_parl]["nationalPoliticalGroup"]
        if this_npg not in npg_found:
            npg_found.append(this_npg)
        parl_data[one_parl]["nationalPoliticalGroup"] = npg_found.index(this_npg)
    return (parl_data, npg_found)


def extract_pg(parl_data):
    """Extract political group and replace it in dictionary

    Args:
        parl_data (dict): parliamentarian information

    Returns:
        (dict, list): result of replacement and list of political groups
    """
    pg_found = []
    for one_parl in parl_data.keys():
        this_pg = parl_data[one_parl]["politicalGroup"]
        if this_pg not in pg_found:
            pg_found.append(this_pg)
        parl_data[one_parl]["politicalGroup"] = pg_found.index(this_pg)
    return (parl_data, pg_found)


def pg_join_data_abr(pg_data, pg_abr_data):
    """merge political group data to get the abbreviation for each name

    Args:
        pg_data (list): List of political group name (sorted according to parliamentarian data)
        pg_abr_data (list(tuple)): List of (name, abbrevation)

    Returns:
        list(tuple): List(name, abbreviation)
    """
    merge_result = []
    for this_pg in pg_data:
        for this_abr_pg in pg_abr_data:
            if this_pg == this_abr_pg[0]:
                merge_result.append((this_pg, this_abr_pg[1]))
    return merge_result

def write_json(filepath, dict_data):
    """Write dictionary data in a json file

    Args:
        filepath (str): filepath to the targeted file
        dict_data (dict): dictionary to write into json
    """
    with open(filepath, "w") as json_file:
        json.dump(dict_data, json_file)

def write_pg(filepath, tuple_list):
    """Write csv file from a list of tuples

    Args:
        filepath (str): filepath to the targeted file
        tuple_list (list(tuple)): political group information
    """
    csv_text = ""
    pg_index = 0
    for this_pg in tuple_list:
        csv_text += "{},{}\n".format(pg_index, ",".join(this_pg))
        pg_index += 1
    with open(filepath, "w") as pg_file:
        pg_file.write(csv_text)


def write_item_list(filepath, list_data):
    """Write csv file from list with their index

    Args:
        filepath (str): filepath to the targeted file
        list_data (list): List of item (country, national political group)
    """
    csv_text = ""
    for dt_index in range(len(list_data)):
        csv_text += "{},{}\n".format(str(dt_index), list_data[dt_index])
    with open(filepath, "w") as csv_file:
        csv_file.write(csv_text)


if __name__ == "__main__":
    all_parl_data = parse_parl_file()
    pg_created_data = pg_created_file()
    parl_ctr, country_data = extract_country(all_parl_data)
    parl_pg_ctr, pg_data = extract_pg(parl_ctr)
    abr_pg_data = pg_join_data_abr(pg_data=pg_data, pg_abr_data=pg_created_data)

    parl_npg_pg_ctr, npg_data = extract_npg(parl_pg_ctr)

    tgt_dir = "tmp/stage_2/"
    today_date = datetime.now().strftime("%y%m%d")
    write_json(tgt_dir+"parliamentarian_info_{}.json".format(today_date), parl_npg_pg_ctr)

    write_pg(tgt_dir + "political_group_info.csv", abr_pg_data)
    write_item_list(tgt_dir + "national_political_group_info.csv", npg_data)
    write_item_list(tgt_dir + "country_info.csv", country_data)
    
