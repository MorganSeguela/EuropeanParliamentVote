#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# The goal of this program is to create a transcodification file between parliamentarian information
# and seat information

# Directory and file management
import os

# Manage json file
import json

# Log package
import logging


import time

import math as m


def gen_parliamentarian_info_files():
    """Generator of filepath of parliamentarian info from tmp/stage_1/ directory

    Yields:
        string: filepath to one parliamentarian information file
    """
    main_dir = "tmp/stage_1/"
    parl_files = [parl_info_file for parl_info_file in os.listdir(main_dir) if "parliamentarian_main_info" in parl_info_file]
    for parl_file in parl_files:
        yield main_dir + parl_file


def retrieve_parliamentarian_info():
    """Retrieve all parliamentarian information from stored files

    Return:
        dict: {parl_id: parl_name}
    """    
    parl_info = {}
    for parl_file in gen_parliamentarian_info_files():
        with open(parl_file, "r") as parl_content:
            parl_data = json.load(parl_content)
            for parl_id in parl_data.keys():
                parl_info[parl_id] = parl_data[parl_id]["fullName"]
    return parl_info


def gen_seat_info_files():
    """Filepath generator of seat information 

    Yields:
        string: filepath to the seat information
    """
    main_dir = "tmp/stage_1/"
    seat_files = [seat_info_file for seat_info_file in os.listdir(main_dir) if
                  "parl_PLAN" in seat_info_file]
    for seat_file in seat_files:
        yield main_dir + seat_file


def retrieve_seat_info():
    """Retrieve seat information from tmp/stage_1/

    Returns:
        dict: {parl_date: dict{seat_name: seat_number}}
            parl_date: Concatenation of parliament abbreviation and place date 
            seat_name: parliamentarian name on the seat
            seat_number: seat id
    """
    seat_info = {}
    for seat_file in gen_seat_info_files():
        # Parl_date construction
        filename = seat_file.split("/")[-1]
        seat_date = filename.split("_")[-1][0:6]
        parliament = filename.split("_")[2]

        seat_cur_data = {}
        with open(seat_file, "r") as seat_content:
            for line in seat_content.readlines():
                seat_number, seat_name = line.rstrip().split(",")
                seat_cur_data[seat_name] = seat_number

        parliament_date_key = "{}_{}".format(parliament, seat_date)
        seat_info[parliament_date_key] = seat_cur_data

    return seat_info
              
        

def surname_name_treatment(surname_name):
    """Cleaning website parliamentarian name to match with the pdf one.
        To do so, we put the name first and the surname at the end and we up it
        If the parliamentarian as multiple surname, we only take the first one, and the other are removed

    Returns:
        string; Cleaned website name  
    """
    return " ".join(surname_name.split(" ")[1:]) + " " + surname_name.split(" ")[0].upper()


def rem_more_surname(name):
    """Remove word (part of names) that does not only have upper letters

    Args:
        name (string): Website parliamentarian name

    Returns:
        string: cleaned name with only upper letters
    """
    result_upper_name = []
    save_name = name.split(" ").pop()
    for part_name in name.split(" "):
        index_letter = 0
        isupper = True
        # We verify each letter because "[A-Z]\." is upper and not "."
        while isupper and index_letter < len(part_name):
            # Reminder that a "." is not upper so it also remove "[A-Z]\." name part
            isupper = part_name[index_letter].isupper()
            if isupper:
                index_letter += 1
        if index_letter == len(part_name):
            result_upper_name.append(part_name)
    result_upper_name.append(save_name)
    return " ".join(result_upper_name)


def comp_dist_string(name1, name2):
    """Process the distance between two names by comparing their letters
        Here, each well positioned letter add 1 and -2 otherwise to  avoid retrieving shortest name/longest name

    Args:
        name1 (string): Parliamentarian name for one source
        name2 (string): Parliamentarian name for another source

    Returns:
        float: result of the distance between these 2 names
    """
    if len(name1) > len(name2):
        name2, name1 = (name1, name2)
    result_dist = 0
    for index_l in range(len(name1)):
        if name1[index_l] == name2[index_l]:
            result_dist += 1
        else:
            result_dist -= 2
    return result_dist/len(name2)


def find_closest_name(name, list_names):
    """Compare a target name and a list of names and retrieve the name from the list that is the closest to the targeted one

    Args:
        name (String): target name
        list_names (list[String]): List of name to compare

    Returns:
        (String, Float): (Result_name, Result_distance)
    """
    result_dist = -999
    result_name = ""
    for comp_name in list_names:
        cur_dist = comp_dist_string(name, comp_name)
        if cur_dist == result_dist and cur_dist > 0:
            logging.warning("Warning dist duplicate:\n{} - {} = {}\n{} - {} = {}".format(result_name, name, result_dist, comp_name, name, cur_dist))
        if cur_dist > result_dist:
            result_dist = cur_dist
            result_name = comp_name
    return (result_name, result_dist)


def reverse_parl_info(parl_info):
    """Reverse key-value order from a dictionary
    It raises a warning when a name is duplicated

    Args:
        parl_info (dict): {parl_id: parl_name}

    Returns:
        dict: {parl_name: parl_id}
    """
    reverse_parl_info = {}
    nb_duplicates = 0
    for parl_id in parl_info.keys():
        name = surname_name_treatment(parl_info[parl_id])
        if parl_id in ["197556", "124806"]:
            print("parl_id: {} -- {} => {}".format(parl_id, parl_info[parl_id], name))
            time.sleep(5)
        if name in reverse_parl_info.keys():
            logging.warning("warning duplicate: {}:{} and {}:{}".format(name, parl_id, name, reverse_parl_info[name]))
            nb_duplicates += 1
            name += str(nb_duplicates)
        reverse_parl_info[name] = parl_id
    return reverse_parl_info


def merge_seat_parliamentarian(parl_info, seat_info):
    """Try to merge website parliamentarian name from website and pdf to get parliamentarian id and their seat

    Args:
        parl_info (dict): {paril_id: parl_name}
        seat_info (dict): {parl_date: {parl_name: seat_number}}

    Returns:
        dict: {parl_date: List[(parl_id, parl_name, pdf_parl_name, seat_number)]}
    """
    reversed_parl_info = reverse_parl_info(parl_info)
    success_dict = {}
    fail_dict = {}

    for parl_date in seat_info.keys():
        parl_date_data = seat_info[parl_date]
        pdf_values_name = parl_date_data.keys()

        success_result = []
        fail_result = []

        for pdf_name in pdf_values_name:
            # We send a string length sorted list so smaller name will come first
            name_list_sort = list(reversed_parl_info.keys())
            name_list_sort.sort(key=len)

            result_name, result_dist = find_closest_name(pdf_name, name_list_sort)
            
            #If the distanc score is lower than 0.25 (arbitrary here) it means that it most likely to be failed fail
            if result_dist > 0.25:
                success_result.append((reversed_parl_info[result_name], result_name, pdf_name, parl_date_data[pdf_name], str(result_dist)))
            else:
                fail_result.append((reversed_parl_info[result_name], result_name, pdf_name, parl_date_data[pdf_name], str(result_dist)))

        success_dict[parl_date] = success_result
        fail_dict[parl_date] = fail_result
    
    return (success_dict, fail_dict)


def write_result(type, result_dict):
    """Write result in a csv file inside the tmp/stage_2/ directory

    Args:
        type (String): Type of csv file (fail or success)
        result_dict (dict): {parl_date:List[(parl_id, web_parl_name, pdf_parl_name, seat_number)]}
    """
    result_dir = "tmp/stage_2/"
    for parl_date in result_dict.keys():
        file_name = type + "_" + parl_date + ".csv"
        text_to_write = "\n".join([",".join(transco_tuple) for transco_tuple in result_dict[parl_date]])
        with open(result_dir + file_name, "w") as write_csv_parl:
            write_csv_parl.write(text_to_write)



if __name__ == '__main__':
    parl_info = retrieve_parliamentarian_info()
    seat_info = retrieve_seat_info()
    success_dict, fail_dict = merge_seat_parliamentarian(parl_info, seat_info)
    write_result("fail", fail_dict)
    write_result("success", success_dict)
