import PyPDF2 as pypdf
import re
import requests as rq
import io

# URL of bruxell's plan
bru_plan_url = "https://www.europarl.europa.eu/sedcms/pubfile/HEMICYCLE/PLAN_BRU.pdf"
# URL of strasbourg's plan
str_plan_url = "https://www.europarl.europa.eu/sedcms/pubfile/HEMICYCLE/PLAN_STR.pdf"

def get_parl_place(plan_pdf):
    """Get place number of parliementary

    Args:
        plan_pdf (pdfObject): result of pypdf parsing of plans parsing

    Returns:
        dict: {name: place_id}
    """
    place_in_parl = {}
    first_page_text = re.sub("[\t\r ]+","", plan_pdf.pages[0].extract_text(0))

    for name_place in re.findall("[^\d.]+\.+\d+", first_page_text):
        place_in_parl[re.sub("\n", "", name_place.split(".")[0])] = name_place.split(".")[-1]

    return place_in_parl


def get_all_parl_place():
    """Get place number of parliementary for each plan

    Returns:
        dict: {place:dict{name:place}}
    """
    all_plan = {}

    bru_plan_web = rq.get(bru_plan_url)
    bru_plan_mem = io.BytesIO(bru_plan_web.content)
    bru_plan_pdf = pypdf.PdfReader(bru_plan_mem)

    str_plan_web = rq.get(str_plan_url)
    str_plan_mem = io.BytesIO(str_plan_web.content)
    str_plan_pdf = pypdf.PdfReader(str_plan_mem)

    all_plan["BRU"] = get_parl_place(str_plan_pdf)
    all_plan["STR"] = get_parl_place(str_plan_pdf)

    return all_plan

print(get_all_parl_place())



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