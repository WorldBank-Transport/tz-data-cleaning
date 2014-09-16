#!/usr/bin/env python

# usage: Run `python merge_school_locations.py <path/to/baseline.csv> <path/to/location.csv>` via command line
# Dependancies: Mongodb & pymongo
# Both files need to have name, district and school_type columns and the location file needs longitude and latitude fields
# Mongodb was used to simplify querying

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


def merge_schools_coordinates(source, db_name=db_name, collection_name=collection_name):
    """Add coordinates to the schools colection based on
    source csv file. The merging is based on the name, school_type and
    district. The source csv should contain name, district,
    school_type, Longitude and Latitude columns."""
    # Track number of items merged
    items_merged = 0
    # Read the source csv
    source_file = open(source, 'r')
    reader = csv.DictReader(source_file)
    # Loop through each row
    for row in reader:
        query = {}
        # Read school name query
        query['name'] = re.compile(re.escape(row.get('name', 'Unknown name')), re.IGNORECASE)
        # Read district query
        query['district'] = re.compile(re.escape(row.get('district', 'Unknown district')), re.IGNORECASE)
        # Read school type quey
        query['school_type'] = re.compile(re.escape(row.get('school_type', 'Unknown type')), re.IGNORECASE)
        # Read coordinates
        longitude = row.get('longitude')
        latitude = row.get('latitude')
        if longitude and latitude:
            # Check number of matching items
            db = pymongo.MongoClient()[db_name]
            count = db[collection_name].find(query).count()
            # if there is only one item update that item
            if count == 1:
                try:
                    db[collection_name].update(
                        query, {'$set':{ 'longitude': float(longitude),
                        'latitude': float(latitude)}}, upsert=False)
                    items_merged  += 1
                except:
                    pprint("Couldn't merge item\n")
                    pprint(row)
    return items_merged


def export_csv(outfile, db_name=db_name, collection_name=collection_name):
    """Export csv form mongodb"""
    export_command = ['mongoexport', '--db', db_name,
                      '--collection', collection_name, '--csv',
                      '--fieldFile', 'fields.txt',
                      '--out', outfile]
    subprocess.call(export_command)


if __name__ == '__main__':

    if len(sys.argv) >= 3:
        outfile = 'out_' + sys.argv[1]
        import_to_mongo(sys.argv[1])
        pprint(merge_schools_coordinates(sys.argv[2]))
        export_csv(outfile)
        pprint('******\nOutput written to %s.******' %outfile)
    else:
        pprint('**Insufficient arguments**')
