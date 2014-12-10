#!/usr/bin/env python

# usage: Run
# `python merge_school_codes.py <non-coded.csv> <coded.csv> <output-fields-file>`.
# `<non-coded.csv>`: path to csv file which you want to introduce a codes column.
# `<coded.csv>`: path to csv file where codes column codes can be extracted from.
# '<output-fields-file>': path to a text file that defines list of output fields
# each separated by a newline.
# Dependancies: Python, Mongodb & pymongo
# Mongodb was used to simplify querying
# TODO: Create a generic script for merging csv based on this algorithm
# TODO: Check the posibility of using Pandas instead of mongodb  

import csv
import re
import sys
from pprint import pprint
import pymongo
import subprocess

db_name = 'data_cleaning'
collection_name = 'dataset'

def import_to_mongo(source, db_name=db_name, collection_name=collection_name):
    """Save the csv in mongodb"""
    pymongo.MongoClient()[db_name][collection_name].remove()
    
    import_command = ['mongoimport', '--db', db_name,
                      '--collection', collection_name, '--type', 'csv',
                      '--headerline', '--file', source]
    subprocess.call(import_command)


def merge_schools_codes(source, db_name=db_name,
                        collection_name=collection_name):
    """Add school codes to the schools collection based on
    source csv file. The merging is based on the name, school_type and
    district. The source csv should contain name, district,
    school_type and code columns."""
    # Track number of items merged
    items_merged = 0
    # Read the source csv
    source_file = open(source, 'r')
    reader = csv.DictReader(source_file)
    # Loop through each row
    for row in reader:
        query = {}
        # Read school name query
        query['name'] = re.compile(
            re.escape(unicode(row.get('name', 'Unknown name'), 'utf-8')),
            re.IGNORECASE)
        # Read district queryfields.txt'
        query['district'] = re.compile(
            re.escape(unicode(row.get('district', 'Unknown district'), 'utf-8')),
            re.IGNORECASE)
        # Read school type query
        query['school_type'] = re.compile(
            re.escape(unicode(row.get('school_type', 'Unknown type'), 'utf-8')),
            re.IGNORECASE)
        code = unicode(row.get('code', ''), 'utf-8')
        # Check number of matching items
        db = pymongo.MongoClient()[db_name]
        count = db[collection_name].find(query).count()
        # if there is only one item update that item
        if count == 1:
            try:
                db[collection_name].update(
                    query, {'$set':{ 'code': code}}, upsert=False)
                items_merged  += 1
            except:
                pprint("Couldn't merge item\n")
                pprint(row)
    return items_merged


def export_csv(outfile, fields, db_name=db_name,
               collection_name=collection_name):
    """Export csv form mongodb"""
    export_command = ['mongoexport', '--db', db_name,
                      '--collection', collection_name, '--csv',
                      '--fieldFile', fields,
                      '--out', outfile]
    subprocess.call(export_command)


if __name__ == '__main__':

    if len(sys.argv) >= 3:
        outfile = sys.argv[1] + '-out.csv'
        import_to_mongo(sys.argv[1])
        pprint(merge_schools_codes(sys.argv[2]))
        if len(sys.argv) >= 4:
            fields_file = sys.argv[3]
        else:
            fields_file = 'fields.txt'
        export_csv(outfile, fields_file)
        pprint('******\nOutput written to %s.******' %outfile)
    else:
        pprint('**Insufficient arguments**')
