#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# File management
import os

# Regex
import re

# Json package
import json

# Datetime manipulation
from datetime import datetime


def vote_files():
    """Generator of vote data files in tmp/stage_1/

    Yields:
        str: filepath to vote data
    """
    start_dir = "tmp/stage_1/"
    vote_files = [vote_file for vote_file in os.listdir(start_dir) if re.match("^Vote", vote_file)]
    for one_file in vote_files:
        yield start_dir + one_file


def parse_vote_file():
    """Retrieve all vote data

    Returns:
        List[Dict]: List of dictionnary that contains vote information
    """
    votes_data = []
    for vote_file in vote_files():
        with open(vote_file, "r") as vote_content:
            cur_data = json.load(vote_content)["data"]
            votes_data.extend(cur_data)
    return votes_data


def extract_minute(votes_data):
    """Extract minute data and replace minute information with minute id

    Args:
        votes_data (list[Dict]): Vote data

    Returns:
        (List[Dict], List): List of data vote and List of minute URLs
    """
    pv_found = []
    new_votes_data = []
    for one_vote in votes_data:
        this_url = one_vote["url"][1]
        
        if this_url not in pv_found:
            pv_found.append(this_url)
        del one_vote["url"]

        one_vote["PV"] = pv_found.index(this_url)
        new_votes_data.append(one_vote)
    return (new_votes_data, pv_found)


def extract_vote_content(votes_data):
    """Extract vote content information (description, time) and remove these information

    Args:
        votes_data (List[Dict]): Vote data

    Returns:
        (List[Dict], Dict): (List of vote information, content_data)
    """
    content_data = {}
    new_votes_data = []

    for one_vote in votes_data:
        content_id = one_vote["id"]
        if content_id not in content_data.keys():
            cur_data = {
                "reference": one_vote["reference"],
                "date": one_vote["date"],
                "PV": one_vote["PV"],
                "description" : one_vote["description"]
                }
            content_data[content_id] = cur_data
        del one_vote["reference"], one_vote["date"], one_vote["PV"], one_vote["description"]
        new_votes_data.append(one_vote)
    return (new_votes_data, content_data)


def extract_vote_result(vote_data):
    """Extract parliamentarian id for votes and intentions

    Args:
        vote_data (List[Dict]): Vote data

    Returns:
        dict: Results for each content id
    """
    list_vote_values = ["forDetails", "againstDetails", "abstentionDetails"]
    list_int_values = ["For", "Against", "Abstention"]
    result_content_vote = {}

    for vote_content in vote_data:
        vote_result = {}
        for vote_value in list_vote_values:
            cur_member = {}
            if vote_value in vote_content.keys():
                pgs = vote_content[vote_value]
                for pg in pgs.keys():
                    members = pgs[pg]
                    for member in members:
                        cur_member[member["PersId"]] = member["Name"]
            vote_result[list_vote_values.index(vote_value)] = cur_member
        intention_result = {}
        if "intentions" in vote_content.keys():
            for int_val in vote_content["intentions"].keys():
                members  = vote_content["intentions"][int_val]
                cur_member = {}
                for member in members:
                    cur_member[member["PersId"]] = member["Name"]
                intention_result[list_int_values.index(int_val)] = cur_member
        result_content_vote[vote_content["id"]] = {"vote": vote_result, "intention": intention_result}
    
    return result_content_vote

def write_json(filepath, data_json):
    """Dump dict in JSON

    Args:
        filepath (str): filepath to json file
        data_json (Dict): Dictionary to dump into json
    """
    with open(filepath, "w") as json_file:
        json.dump(data_json, json_file)


def write_csv(filepath, list_item):
    """Write minutes information in csv

    Args:
        filepath (str): filepath to write file
        list_item (List[List]): List of tuple
    """
    csv_text = ""
    for url_index in range(len(list_item)):
        csv_text += "{},{}\n".format(url_index, list_item[url_index])

    with open(filepath, "w") as csv_file:
        csv_file.write(csv_text)


if __name__ == "__main__":
    all_votes_data = parse_vote_file()
    votes_pv, pv_found =  extract_minute(all_votes_data)
    votes_con_pv, con_found = extract_vote_content(votes_pv)
    clean_votes = extract_vote_result(votes_con_pv)


    tgt_dir = "tmp/stage_2/"

    today_date = datetime.now().strftime("%y%m%d")
    
    write_json(tgt_dir + "Vote_data_{}.json".format(today_date), clean_votes)
    write_json(tgt_dir + "Vote_content_{}.json".format(today_date), con_found)
    write_csv(tgt_dir + "PV_url_{}.csv".format(today_date), pv_found)

