#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# The goal of this program is to retrieve parliament plan with parliamentarian
# We retrieve seat number and the parliamentarian name associated

# Log package
import logging

# Access website
import requests as rq

# Store file in memory
import io

# Regex to extract date, seat_id and parliamentarian name
import re

# Package to parse and write date
from datetime import datetime

# Package to parse pdf filess
import PyPDF2 as pypdf



def generator_plan():
    """Generator of parliaments plans: "PLAN_STR" (Strasbourg) and "PLAN_BRU" (Brussels)

    Yields:
        str: Plan name
    """
    parl_plans = ["PLAN_STR", "PLAN_BRU"]
    for plan in parl_plans:
        yield plan


def retrieve_plan_pdf(plan_url):
    """Retrieve parliament plan pd from european parliament website
    We choose the pdf plan as it permits to place all parliamentarian, 
    unlike the interactive map which places only those who was there.

    Args:
        plan_url (str): url to access the plan pdf

    Returns:
        bytes: content of the webpage
    """
    plan_html = rq.get(plan_url)
    
    return plan_html.content


def store_current_plan(plan_html_content, filepath):
    """Store the current pdf plan in tmp/

    Args:
        plan_html_content (bytes): Content of the pdf
        filepath (str): filepath to where write data
    """
    with open(filepath, "wb") as write_pdf:
        write_pdf.write(plan_html_content)
    logging.info("Saving pdf in {}".format(filepath))


def store_parl_seat_data(dict_parl_seat, filepath):
    """Store data retrieved in a csv in tmp/

    Args:
        dict_parl_seat (dict): data retrieve from pdf {seat_id: parl_name}
        filepath (str): filepath where to write data
    """
    all_data_str = ""
    for seat_id in dict_parl_seat.keys():
        all_data_str += "{},{}\n".format(seat_id, dict_parl_seat[seat_id])
    
    with open(filepath, "w") as write_csv:
        write_csv.write(all_data_str)
    logging.info("Saving retrieved data in {}".format(filepath))


def get_parl_place(plan_pdf):
    """Retrieve data from parsed pdf.
    It retrieves the date when places was given,
    and the parliamentarian attribution of each seat.

    Args:
        plan_pdf (pdfObject): Parsed pdf data

    Returns:
        (str, dict): (place_date, parl_seat)
            place_date: string that correspond to the date places where given
            parl_seat : {seat_id, parliamentarian name}
    """

    place_in_parl = {}
    first_page_text = plan_pdf.pages[0].extract_text(0)

    place_date = re.findall(r"\d+\.\d+\.\d+", first_page_text)[0]
    
    # replace spaces in names with _
    first_page_high_name = re.sub(r"(\w+) ", r"\g<1>_", first_page_text)
    
    # remove underscore between name and point
    first_page_rem_und_to_space = re.sub(r"_\W", "", first_page_high_name)

    # remove all kind of space (not newline)
    first_page_rem_sp = re.sub(r"[\r\t ]+", "", first_page_rem_und_to_space)

    # Extract string like name...999
    for name_place in re.findall("[^\d.]+\.+\d+", first_page_rem_sp):
        name_with_space = re.sub("_", " ", name_place)
        place_in_parl[name_with_space.split(".")[-1]] = re.sub("\n|^ ", "", name_with_space.split(".")[0])

    return (place_date, place_in_parl)


def parse_plan_pdf(plan_html_content):
    """Store the pdf plan in memory and parse the pdf file.
    Storing this file in memory permits pdfReader to read this file.
    It is impossible otherwise.

    Args:
        plan_html_content (bytes): pdf plan content

    Returns:
        (str, dict): (place_date, parl_seat)
            place_date: string that correspond to the date places where given
            parl_seat : {seat_id, parliamentarian name}
    """
    plan_mem = io.BytesIO(plan_html_content)
    plan_pdf = pypdf.PdfReader(plan_mem)
    
    return get_parl_place(plan_pdf=plan_pdf)


if __name__ == "__main__":
    """
    Running this file permits to retrieve earliest parliament plan to gather which parliamentarian is on which seat.
    To do so, we download the pdf plan from the european parliament website, make a save in tmp/, parse it and store the result in tmp/

    We chose to use the pdf from the website as it includes all current parliamentarian, unlike the interactive
    map which excludes parliamentarian that are not present.
    """
    for parl_plan in generator_plan():
        cur_url = "https://www.europarl.europa.eu/sedcms/pubfile/HEMICYCLE/{}.pdf".format(parl_plan)
        plan_content = retrieve_plan_pdf(cur_url)

        save_pdf_filepath = "tmp/stage_1/" + parl_plan + "_{}.pdf".format(datetime.today().strftime("%y%m%d"))
        store_current_plan(plan_html_content=plan_content, filepath=save_pdf_filepath)


        place_date, parl_seat_data = parse_plan_pdf(plan_content)
        filepath = "tmp/stage_1/parl_" + parl_plan + "_{}.csv".format(datetime.strptime(place_date, "%d.%m.%Y").strftime("%y%m%d"))
        store_parl_seat_data(parl_seat_data, filepath)
