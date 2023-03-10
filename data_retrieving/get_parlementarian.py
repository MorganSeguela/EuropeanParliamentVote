from unicodedata import name
import PyPDF2 as pypdf
from bs4 import BeautifulSoup as bs

import re
import requests as rq
import io

from datetime import datetime

import json

# URL of bruxell's plan
bru_plan_url = "https://www.europarl.europa.eu/sedcms/pubfile/HEMICYCLE/PLAN_BRU.pdf"
# URL of strasbourg's plan
str_plan_url = "https://www.europarl.europa.eu/sedcms/pubfile/HEMICYCLE/PLAN_STR.pdf"
# URL of parlementary list
parl_list_url = "https://www.europarl.europa.eu/meps/en/full-list/xml/"

def get_parl_place(plan_pdf):
    """Get place number of parliementary

    Args:
        plan_pdf (pdfObject): result of pypdf parsing of plans parsing

    Returns:
        dict: {place_id: name}
    """
    place_in_parl = {}
    first_page_text = plan_pdf.pages[0].extract_text(0)

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

    return place_in_parl


def get_all_parl_place(save_dir = "../EP_project/"):
    """Get place number of parliementary for each plan

    Returns:
        dict: {plan: dict{place:name}}
    """
    all_plan = {}

    bru_plan_web = rq.get(bru_plan_url)
    bru_plan_mem = io.BytesIO(bru_plan_web.content)
    bru_plan_pdf = pypdf.PdfReader(bru_plan_mem)

    str_plan_web = rq.get(str_plan_url)
    str_plan_mem = io.BytesIO(str_plan_web.content)
    str_plan_pdf = pypdf.PdfReader(str_plan_mem)

    string_date = datetime.today().strftime("%y%m%d")
    with open(save_dir + "map/PLAN_BRU_"+ string_date + ".pdf", "wb") as save_bru:
        save_bru.write(bru_plan_web.content)
    
    with open(save_dir + "map/PLAN_STR_"+ string_date + ".pdf", "wb") as save_str:
        save_str.write(str_plan_web.content)

    all_plan["BRU"] = get_parl_place(bru_plan_pdf)
    all_plan["STR"] = get_parl_place(str_plan_pdf)

    return all_plan

def get_parl_main_info():
    parl_info = {}

    parl_list_xml = rq.get(parl_list_url)
    parl_parsed_xml = bs(parl_list_xml.content, "xml")

    for parl_pers in parl_parsed_xml.meps.children:
        id = parl_pers.id.string
        parl_info[id] = {}
        for info in parl_pers.children:
            if info.name != "id":
                parl_info[id][info.name] = info.string
    return parl_info


def get_parl_info(filepath_transco = "../EP_project/transco/"):
    """Get list of all parlementary 

    Returns:
        dict: {id:{info}}
        info :
            fullname: (string) -- Full name of parlementary
            country: (string) -- Country of the parlementary
            politicalGroup: (string) -- Political group in EP
            nationalPoliticalGroup: (string) -- Political group in country
            STR_siege: (string) -- Siege number in Strasbourg
            BRU_siege : (string) -- Siege number in Brussel 
    """
    parl_info = {}

    parl_list_xml = rq.get(parl_list_url)
    parl_parsed_xml = bs(parl_list_xml.content, "xml")

    for parl_pers in parl_parsed_xml.meps.children:
        id = parl_pers.id.string
        parl_info[id] = {}
        for info in parl_pers.children:
            if info.name != "id":
                parl_info[id][info.name] = info.string
    
    string_date = datetime.today().strftime("%y%m%d")
    with open(filepath_transco + "corrected_transco_parl_bru_" + string_date + ".csv", "r") as transco_bru:
        transco_bru.readline()
        for transco_line in transco_bru.readlines():
            parl_id, siege_id, name_surname, siege_name = re.sub("\n", "", transco_line).split(",")
            parl_info[parl_id]["BRU_siege"] = siege_id

    with open(filepath_transco + "corrected_transco_parl_str_" + string_date + ".csv", "r") as transco_str:
        transco_str.readline()
        for transco_line in transco_str.readlines():
            parl_id, siege_id, name_surname, siege_name = re.sub("\n", "", transco_line).split(",")
            parl_info[parl_id]["STR_siege"] = siege_id

    return parl_info


if __name__ == "__main__":
    filepath_transco = "../EP_project/transco/"
    info_parl = get_parl_info()
    
    string_date = datetime.today().strftime("%y%m%d")
    json_filename = "tmp/Parlementarian_"+ string_date + ".json"
    with open(json_filename, "w") as json_file:
        json.dump(info_parl,json_file)
