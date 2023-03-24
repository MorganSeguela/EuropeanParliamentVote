#!/usr/bin/env python3

# Version: V0.1
# Author : Morgan Séguéla

# To do: Trying to retrieve planning from the calendar in the website

# Parse html
from bs4 import BeautifulSoup as bs

# Retrieve website
import requests as rq

# Regex package
import re


def retrieve_agenda_html(agenda_url):
    """Retrieve the European Parliament agenda website

    Args:
        agenda_url (str): url to get the European Parliament Agenda

    Returns:
        str: HTML content of the EP agenda
    """
    agenda_html = rq.get(agenda_url)
    return agenda_html.content


def retrieve_week_planning(agenda_parsed):
    """Retrieve the parsed html for each week from the parsed agenda

    Args:
        agenda_parsed (BeautifulSoup): Parsed html of the agenda

    Yields:
        BeautifulSoup: Parsed html of the week
    """
    # Each week is in a listcontent
    main_content = agenda_parsed.html.body.find_all(attrs={'class':'listcontent'})

    for week in main_content:
        yield week



def retrieve_day_url(parsed_week):
    """Retrieve the day and the url to parse vote for each week

    Args:
        parsed_week (BeautifulSoup): Parsed week html that contains all data

    Returns:
        List[Vect]: List of vector that contains (day, url) 
    """
    isH4 = True
    day = ""
    info = ""

    list_vect = []
    
    # Information are alternatively in h4 and ul-li tag
    for tchild in parsed_week.children:
        
        # The day string is in the h4 tag
        if tchild.name == "h4":
            day = re.sub("[\t\r\n]+","", tchild.string)
            isH4 = False

        # All urls of the day is in ul
        elif tchild.name == "ul":
            # We have to be carefull as text is also consider as child
            if tchild.li.span != None:

                # The 1st li links to a pdf, 2nd links to the right xml
                vote_url = tchild.li.span.find_all("a")[1]['href']
                isH4 = True

                # Verify if the second is the xml
                if re.search("\.xml",vote_url):
                    info = vote_url
                else: 
                    print("Il y a un pb avec XML")
        # If tag unknown
        else:
            if tchild.name != None:
                print(str(tchild.name) + "inconnu")
        # Reset if all information gathered
        if isH4 and day and info:
            list_vect.append((day, info))
            day = ""
            info = ""
    return list_vect


def retrieve_planning_urls(agenda_content):
    """Retrieve all days and urls associated to the vote of this day

    Args:
        agenda_content (BeautifulSoup): Parsed html of the agenda website

    Returns:
        List[Vect]: List of all days and urls from the parsed agenda
    """
    parsed_agenda = bs(agenda_content, 'html.parser')

    all_url_agenda = []

    for week in retrieve_week_planning(parsed_agenda):
        all_url_agenda.extend(retrieve_day_url(week))
    return all_url_agenda

def gen_stage():
    """Stage directory generator

    Yields:
        str: Directory name between "stage_1", "stage_2"
    """
    all_stages = ["stage_1", "stage_2"]
    for stage in all_stages:
        yield stage

def write_days_urls_data(list_vect_data, filepath):
    """Write in a file the retrieved data

    Args:
        list_vect_data (List[Vect]): List of all days and urls associated
        filepath (str): filepath to the file where to write
    """
    already_parsed = []
    
    for cur_stage in gen_stage():
        cur_filepath = "tmp/{}/{}".format(cur_stage,filepath)
        with open(cur_filepath, "r") as read_file:
            already_parsed.extend([data_str.rstrip().split(",")[0] for data_str in read_file.readlines()])

    already_parsed

    str_all_data = ""
    for vect_data in list_vect_data:
        if vect_data[0] not in already_parsed: 
            str_all_data += ",".join(vect_data) + "\n"

    with open(filepath, "a") as write_file:
        write_file.write(str_all_data)
    


if __name__ == "__main__":
    agenda_url = "https://www.europarl.europa.eu/plenary/fr/votes.html?tab=votes"
    agenda_html = retrieve_agenda_html(agenda_url)
    all_data = retrieve_planning_urls(agenda_html)

    filepath = "days_url_vote.csv"
    write_days_urls_data(all_data, filepath)