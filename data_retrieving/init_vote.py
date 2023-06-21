#!/usr/bin/env python3

# ======================== #
####    Information     ####
# ------------------------ #
# Version   : V1
# Author    : Morgan Séguéla
# Date      : 21/06/2023

####    Objective       ####
# ------------------------ #
# The goal of this program is to retrieve votes informations from the votes xml in planning.

####    TO DO           ####
# ------------------------ #
# ======================== #

# File and Directory management
import os

# Package to retrieve data from the internet
import requests as rq

# Parsing Semi-structured data (html, xml)
from bs4 import BeautifulSoup as bs

# Regex package
import re

# Json file management
import json 

def get_voter_details(group_result):
    """Retrieve voters information from vote

    Args:
        group_result (bs4.element.Tag): Starting node of a group of voters

    Returns:
        list: list of dictionnaries of voters informations
    """
    voters_list = []
    for voter in group_result:
        voter_info = {}
        voter_info["MepId"] = voter["MepId"]
        voter_info["PersId"] = voter["PersId"]
        voter_info["Name"] = voter.string

        voters_list.append(voter_info)

    return voters_list


def get_intention(result_node):
    """Retrieve vote intention from result

    Args:
        result_node (bs4.element.Tag): Starting node of vote intention

    Returns:
        dict: Dictionnary with opinion as key, and a list of voters informations as value
    """
    intention_result = {}

    for intention_opinion in result_node.children:
        if re.search("Intentions.Result.Abstention", intention_opinion.name):
            intention_result["Abstention"] = get_voter_details(intention_opinion)
        
        elif re.search("Intentions.Result.For", intention_opinion.name):
            intention_result["For"] = get_voter_details(intention_opinion)

        if re.search("Intentions.Result.Against", intention_opinion.name):
            intention_result["Against"] = get_voter_details(intention_opinion)

    return intention_result


def get_group_vote_details(result_node):
    """Get group and voters for a vote

    Args:
        result_node (bs4.element.Tag): Node that corresponds to the start of result information Result.*

    Returns:
        dict: Dictionnary with group name as key, and a list of dictionnary of voter informations as content
    """
    voters_group = {}

    for group in result_node.children:
        group_id = group["Identifier"]
        voters_group[group_id] = get_voter_details(group)

    return voters_group


def get_vote_informations(vote_node, source_url):
    """Retrieve all informations of a vote

    Args:
        vote_node (bs4.element.Tag): Node that corresponds to vote result "RollCallVote.Result"

    Returns:
        dict: Dictionnary of all informations
            url: (string) -- url of the result
            id: (string) -- vote identifier
            date: (string) -- vote date
            description: (string) -- text description
            reference (string) -- reference of the text
            forCount: (int) -- number of vote for "For"
            forDetails: (dict) -- details of voter for "For"
            againstCount: (int) -- number of vote for "Against"
            againstDetails: (dict) -- details of voter for "Against"
            abstentionCount: (int) -- number of vote for "Abstention"
            abstentionDetails: (dict) -- details of voter for "Abstention"
            intentions: (dict) -- intentions details
    """
    vote_info = {}
    vote_info["url"] = source_url
    vote_info["id"] = vote_node["Identifier"]
    vote_info["date"] = vote_node["Date"]
    vote_info["reference"] = None

    for vote_details in vote_node.children:
        if re.search("Description.Text", vote_details.name):
            if vote_details.a:
                vote_info["reference"] = vote_details.a["href"].split("/")[1]
            vote_info["description"] = vote_details.text

        if re.search("Result.For", vote_details.name):
            vote_info["forCount"] = vote_details["Number"]
            vote_info["forDetails"] = get_group_vote_details(vote_details)

        if re.search("Result.Against", vote_details.name):
            vote_info["againstCount"] = vote_details["Number"]
            vote_info["againstDetails"] = get_group_vote_details(vote_details)

        if re.search("Result.Abstention", vote_details.name):
            vote_info["abstentionCount"] = vote_details["Number"]
            vote_info["abstentionDetails"] = get_group_vote_details(vote_details)
        
        if re.search("Intentions", vote_details.name):
            vote_info["intentions"] = get_intention(vote_details)

    return vote_info


def retrieve_day_url(src_day_url_pathfile, tgt_day_url_pathfile):
    """Retrieve url xml of votes from file in tmp/stage_1 then place it in tmp/stage_2

    Args:
        src_day_url_pathfile (str): Source file from tmp/stage_1
        tgt_day_url_pathfile (str): Target file from tmp/stage_2

    Returns:
        List[List]: List of [day, url]
    """
    data_read = []
    # Read file from stage_1
    with open(src_day_url_pathfile, "r") as day_url_file:
        data_read = day_url_file.readlines()

    # Retrieve date and url
    data_day_url = [day_url.rstrip().split(",") for day_url in  data_read]

    # Add those date in file in stage_2 to keep trace of already considered day
    with open(tgt_day_url_pathfile, "a") as tgt_save_file:
        tgt_save_file.writelines(data_read)
    
    os.remove(src_day_url_pathfile)

    return data_day_url


def retrieve_parse_vote_xml(vote_url):
    """Retrieve and parse with BeautifulSoup vote url

    Args:
        vote_url (str): URL of votes of the day

    Returns:
        BeautifulSoup: BeautifulSoup parsed votes xml
    """
    return bs(rq.get(vote_url).content, "xml")


def gen_rollcall_vote_of_day(parsed_vote):
    """Retrieve each rollcall of votes during parsed day

    Args:
        parsed_vote (BeautifulSoup): Parsed votes of the day data

    Yields:
        BeautifulSoup: Rollcall.result node
    """
    for pv in parsed_vote.children:
        for rollcall in pv.children:
            if rollcall.name == "RollCallVote.Result":
                yield rollcall

def get_vote_data(parsed_vote, day_url):
    """Retrieve all votes in a day

    Args:
        parsed_vote (BeautifulSoup): One rollcall node
        day_url (str): url to the PV
    """
    all_vote_info = []
    for one_rollcall in gen_rollcall_vote_of_day(parsed_vote):
        all_vote_info.append(get_vote_informations(one_rollcall, day_url))
    return all_vote_info


def write_vote_data(vote_data, tgt_pathfile):
    """Write vote data in stage_2

    Args:
        vote_data (dict): Data retrieved from parsed vote
        tgt_pathfile (str): Target pathfile to write data
    """
    result_dict = {"data":vote_data}
    with open(tgt_pathfile, "w") as json_file:
        json.dump(result_dict,json_file)


if __name__ == "__main__":
    src_file_path = "tmp/stage_1/first_days_url_vote.csv"
    tgt_file_path = "tmp/stage_1/parsed_days_url_vote.csv"
    days_urls = retrieve_day_url(src_file_path, tgt_file_path)

    for day_url in days_urls:
        filepath = "tmp/stage_1/Vote_" + re.sub(" ", "_", day_url[0]) + ".json"
        parsed_vote = retrieve_parse_vote_xml(day_url[1])
        vote_data = get_vote_data(parsed_vote, day_url)
        write_vote_data(vote_data, filepath)
