from bs4 import BeautifulSoup as bs
import requests as rq
import json
import re
import os
# import dateparser as dt

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
            vote_info["description"] = vote_details.string

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


def get_all_vote_in_file(file_url):
    """Parse and extract information from the url in param

    Args:
        file_url (string): url to the vote result (in xml)

    Returns:
        list: list of votes and their details extracted from file
    """
    pv_file = rq.get(file_url)
    parsed_xml = bs(pv_file.content, "xml")

    all_vote_info = []

    for PV in parsed_xml.children:
        i = 0

        for RollCall in PV.children:
            if RollCall.name == "RollCallVote.Result":
                all_vote_info.append(get_vote_informations(RollCall, file_url))
    
    return all_vote_info

def get_all_vote_url(agenda_url):
    """Parse and extract url of XML vote PV

    Args:
        agenda_url (string): url to get the agenda of votes

    Returns:
        dict: "written Date":"url"
    """
    agenda_html = rq.get(agenda_url)
    bs_agenda = bs(agenda_html.content, 'html.parser')
    main_content = bs_agenda.html.body.find_all(attrs={'id':'content_left'})[0]
    weekly_agenda = main_content.find_all(attrs={'class':'expand_collapse'})

    dict_day_url = {}

    for t in weekly_agenda:
        test = t.find_all(attrs={'class':'listcontent'})[0]
        isH4 = True
        day = ""
        info = ""

        for tchild in test.children:
            if tchild.name == "h4":
                day = re.sub("[\t\r\n]+","", tchild.string)
                isH4 = False

            elif tchild.name == "ul":
                vote_url = tchild.li.span.find_all("a")[1]['href']
                isH4 = True

                if re.search("\.xml",vote_url):
                    info = vote_url
                else: 
                    print("Il y a un pb avec XML")
            else:
                if tchild.name != None:
                    print(str(tchild.name) + "inconnu")
            if isH4 and day and info:
                dict_day_url[day] = info
                day = ""
                info = ""

    return dict_day_url
        

if __name__ == "__main__":
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    
    main_vote_html = "https://www.europarl.europa.eu/plenary/fr/votes.html?tab=votes"

    dict_day_url = get_all_vote_url(main_vote_html)

    for key_date in dict_day_url.keys():
        print(key_date)
        current_date_url = dict_day_url[key_date]
        resultat_vote = get_all_vote_in_file(current_date_url)
        
        result_dict = {"data":resultat_vote}
        json_filename = "tmp/Votes_"+"_".join(key_date.split(" ")) + ".json"
        with open(json_filename, "w") as json_file:
            json.dump(result_dict,json_file)

        