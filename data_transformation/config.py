#!/usr/bin/env python3

# Version: V0.2
# Author : Morgan Séguéla

# This program permits to retrieve config data 

from configparser import ConfigParser

def config(filename="database.ini", section="postgresql"):
    # create a parser
    parser = ConfigParser()

    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params =parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    
    else:
        raise Exception('Section {0} not found in the file {1}'.format(section, filename))
    
    return db
