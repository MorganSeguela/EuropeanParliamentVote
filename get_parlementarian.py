from unicodedata import name
import PyPDF2 as pypdf
from bs4 import BeautifulSoup as bs

import re
import requests as rq
import io

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


def get_all_parl_place():
    """Get place number of parliementary for each plan

    Returns:
        dict: {place:dict{name:place}}
        info :
            fullname: (string) -- Full name of parlementary
            country: (string) -- Country of the parlementary
            politicalGroup: (string) -- Political group in EP
            nationalPoliticalGroup: (string) -- Political group in country
    """
    all_plan = {}

    bru_plan_web = rq.get(bru_plan_url)
    bru_plan_mem = io.BytesIO(bru_plan_web.content)
    bru_plan_pdf = pypdf.PdfReader(bru_plan_mem)

    str_plan_web = rq.get(str_plan_url)
    str_plan_mem = io.BytesIO(str_plan_web.content)
    str_plan_pdf = pypdf.PdfReader(str_plan_mem)

    all_plan["BRU"] = get_parl_place(bru_plan_pdf)
    all_plan["STR"] = get_parl_place(str_plan_pdf)

    return all_plan


def get_parl_info():
    """Get list of all parlementary 

    Returns:
        dict: {id:{info}}
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
    
    return parl_info


# print(get_all_parl_place())

# print(get_parl_info())

parl_place = get_all_parl_place()
brux = parl_place["BRU"].copy()
strasb = parl_place["STR"].copy()

print(len(brux))
print(len(strasb))
print(brux)
print(strasb)


parl_info = get_parl_info()

all_parl_info = {}

for parl_id in parl_info.keys():
    parl_info_name = parl_info[parl_id]["fullName"]

    name_surname = " ".join(parl_info_name.split(" ")[1:]) + " " + parl_info_name.split(" ")[0].upper()

    all_parl_info[parl_id] = parl_info[parl_id].copy()

    print(name_surname)

    # bru_all = []
    bru_real_siege = -1
    for bru_siege_id in brux.keys():
        print(bru_siege_id + " - " + brux[bru_siege_id] + "::" + name_surname)
        if name_surname[0:len(brux[bru_siege_id])] == brux[bru_siege_id]:
            # bru_all.append(brux[bru_siege_id])
            bru_real_siege = bru_siege_id
    
    if int(bru_real_siege) > 0:
        all_parl_info[parl_id]["BRU"] = bru_real_siege
        del brux[bru_real_siege]
    else :
        print("WARNING")

    # str_all = []
    str_real_siege = -1
    for str_siege_id in strasb.keys():
        print(str_siege_id + " - " + strasb[str_siege_id] + "::" + name_surname)
        if name_surname[0:len(strasb[str_siege_id])] == strasb[str_siege_id]:
            # str_all.append(strasb[str_siege_id])
            str_real_siege = str_siege_id

    if int(str_real_siege) > 0:
        all_parl_info[parl_id]["STR"] = str_real_siege
        del strasb[str_real_siege]
    else :
        print("WARNING")

print(all_parl_info)

# print(parsed_xml.meps)


# pdf_name = "/home/morgan/Documents/EP_project/PLAN_BRU.pdf"

# pdfobject=open(pdf_name,'rb')
# pdf = pypdf.PdfReader(pdfobject)

# print(get_parl_place_bru(pdf))


# pdf_name = "/home/morgan/Documents/EP_project/PLAN_STR.pdf"

# pdfobject=open(pdf_name,'rb')
# pdf = pypdf.PdfReader(pdfobject)



# page = pdf.pages[0]
# text = page.extract_text(0)
# test = re.sub("[\t\r ]+","", text)

# place_in_parl = {}

# for pouet in re.findall("[^\d.]+\.+\d+", test):
#     place_in_parl[re.sub("\n", "", pouet.split(".")[0])] = pouet.split(".")[-1]

# print(place_in_parl)




## Parlement list website ##
# https://www.europarl.europa.eu/meps/en/full-list/xml/


# print(test)