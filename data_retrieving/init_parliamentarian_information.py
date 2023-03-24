#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# Log package
import logging

# Access and Parse packages 
import requests as rq
from bs4 import BeautifulSoup as bs

# Package to dump json in files
import json

# Package to get the today date when write file
from datetime import datetime


def retrieve_parl_xml(parl_list_url):
    """Retrieve parliamentarians list from the european parliament website.
    This list is an xml document.

    Args:
        parl_list_url (str): URL to the parliamentarians list xml

    Returns:
        str: XML document that contains the parliamentarians list
    """
    logging.warning("Retrieving data from:\n{}\nDo not touch anything".format(parl_list_url))
    parl_list_xml = rq.get(parl_list_url)
    return parl_list_xml


def parse_parl_info(parl_list_xml):
    """Parse the XML document that contains the parliamentarians list.
    It retrieves their id, fullname, country, political group, and their national political group.

    Args:
        parl_list_xml (str): xml document to parse

    Returns:
        dict: {id:{info}}
            info :
                fullname: (string) -- Full name of parlementary
                country: (string) -- Country of the parlementary
                politicalGroup: (string) -- Political group in EP
                nationalPoliticalGroup: (string) -- Political group in country
    """
    parl_info = {}

    parl_parsed_xml = bs(parl_list_xml.content, "xml")

    for parl_pers in parl_parsed_xml.meps.children:
        id = parl_pers.id.string
        parl_info[id] = {}
        for info in parl_pers.children:
            if info.name != "id":
                parl_info[id][info.name] = info.string
    return parl_info


def write_parl_data(dict_data, filepath):
    """Dump the dictionary data into a json file

    Args:
        dict_data (dict): dictionary of parliamentarian data
        filepath (str): filepath where to write data
    """
    with open(filepath, "w") as write_file:
        json.dump(dict_data, write_file)


if __name__ == '__main__':
    # URL of parlementary list
    parl_list_url = "https://www.europarl.europa.eu/meps/en/full-list/xml/"
    parl_list_xml = retrieve_parl_xml(parl_list_url)
    data_parl = parse_parl_info(parl_list_xml)

    write_filepath = "tmp/stage_1/parliamentarian_main_info_{}.json".format(datetime.today().strftime("%y%m%d"))
    write_parl_data(data_parl, write_filepath)
    logging.warning("Retrieving Done")