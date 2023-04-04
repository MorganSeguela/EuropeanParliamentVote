#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# 

import os

import re

import json

from datetime import datetime


def vote_files():
    start_dir = "tmp/stage_1/"
    vote_files = [vote_file for vote_file in os.listdir(start_dir) if re.match("^Vote", vote_file)]
    for one_file in vote_files:
        yield start_dir + one_file


def parse_vote_file():
    votes_data = []
    for vote_file in vote_files():
        with open(vote_file, "r") as vote_content:
            cur_data = json.load(vote_content)["data"]
            votes_data.extend(cur_data)
    return votes_data


def extract_minute(votes_data):
    pv_found = []
    new_votes_data = []
    for one_vote in votes_data:
        this_url = one_vote["url"][1]
        
        if this_url not in pv_found:
            pv_found.append(this_url)
        
        del one_vote["url"]

        one_vote["PV"] = pv_found.index(this_url)
        new_votes_data.append(one_vote)
        # date_url = "-".join(this_url.split("/")[-1].split("-")[2:5])        
        # print(datetime.strptime(date_url, "%Y-%m-%d"))
    return (new_votes_data, pv_found)


def extract_vote_content(votes_data):
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


def write_json(filepath, data_json):
    with open(filepath, "w") as json_file:
        json.dump(data_json, json_file)


def write_csv(filepath, list_item):
    csv_text = ""
    for url_index in range(len(list_item)):
        csv_text += "{},{}\n".format(url_index, list_item[url_index])

    with open(filepath, "w") as csv_file:
        csv_file.write(csv_text)


if __name__ == "__main__":
    all_votes_data = parse_vote_file()
    votes_pv, pv_found =  extract_minute(all_votes_data)
    votes_con_pv, con_found = extract_vote_content(votes_pv)

    tgt_dir = "tmp/stage_2/"

    today_date = datetime.now().strftime("%y%m%d")
    
    write_json(tgt_dir + "Vote_data_{}.json".format(today_date), votes_con_pv)
    write_json(tgt_dir + "Vote_content_{}.json".format(today_date), con_found)
    write_csv(tgt_dir + "PV_url_{}.csv".format(today_date), pv_found)

