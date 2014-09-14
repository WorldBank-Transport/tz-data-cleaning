#!/usr/bin/env python
# usage: Run `python categorize_schools.py <path/to/input-1.csv> ... <path/to/input-n.csv>` via command line

import sys
import re
import csv
import os


# Names maaping, used to map school names to a standard pattern
# eg:- 'Jitihada Sec. school' -> Jitihada Secondary School
# Format: (regex pattern, 'required suffix')
names_mapping = (
    (re.compile('P\/School', re.IGNORECASE), 'Primary School'),
    (re.compile('P\.School', re.IGNORECASE), 'Primary School'),
    (re.compile('P\ School', re.IGNORECASE), 'Primary School'),
    (re.compile('P\ \/School', re.IGNORECASE), 'Primary School'),
    (re.compile('P\/\ School', re.IGNORECASE), 'Primary School'),
    (re.compile('Pr\/\ School', re.IGNORECASE), 'Primary School'),
    (re.compile('P\/Sec', re.IGNORECASE), 'Primary and Secondary School'),
    (re.compile('P\/S', re.IGNORECASE), 'Primary School'),
    (re.compile('Sec\/\ School', re.IGNORECASE), 'Secondary School'),
    (re.compile('Sec\ School', re.IGNORECASE), 'Secondary School'),
    (re.compile('Sec\/\/School', re.IGNORECASE), 'Secondary School'),
    (re.compile('Sec\.School', re.IGNORECASE), 'Secondary School'),
    (re.compile('Sec \.\ School', re.IGNORECASE), 'Secondary School'),
    (re.compile('Pr\.School', re.IGNORECASE), 'Primary School'),
    (re.compile('Pr\ School', re.IGNORECASE), 'Primary School'),
    (re.compile('Pr\/School', re.IGNORECASE), 'Primary School'),
    (re.compile('Sec\.\ School', re.IGNORECASE), 'Secondary School'),
    (re.compile('Sec\/School', re.IGNORECASE), 'Secondary School'),
    (re.compile('Pr\/School', re.IGNORECASE), 'Primary School'),
    (re.compile('Pr\.\ School', re.IGNORECASE), 'Primary School'),
    (re.compile('Pr\ \.\ School', re.IGNORECASE), 'Primary School'),
    (re.compile('S\/Msingi', re.IGNORECASE), 'Primary School'),
    (re.compile('P\/School', re.IGNORECASE), 'Primary School'),
    (re.compile('P\/r\ School', re.IGNORECASE), 'Primary School'),
    (re.compile('P\/r', re.IGNORECASE), 'Primary School'),
    (re.compile('Pr\ \/School', re.IGNORECASE), 'Primary School'),
    (re.compile('S\/S', re.IGNORECASE), 'Secondary School'),
    (re.compile('Sekondary', re.IGNORECASE), 'Secondary'),
    (re.compile('Nusery|Nursary', re.IGNORECASE), 'Nursery'),
    (re.compile('Sc\/school', re.IGNORECASE), 'Secondary'),
    (re.compile('Teacher\ college', re.IGNORECASE), 'Teachers college'),
)


# School type mapping based on school names
# Format: `('school_type', regex pattern)`
categories_mapping = (
    ('secondary', re.compile("secondary|sec|sekondari|seminary|high school|high\/school", re.IGNORECASE)),
    ('primary', re.compile("primary|shule ya msingi", re.IGNORECASE)),
    ('teachers college', re.compile("teachers college|teaching college", re.IGNORECASE)),
    ('university', re.compile("university", re.IGNORECASE)),
    ('nursery', re.compile("nursery|kindergaten|kindergarten|shule ya awali|day care", re.IGNORECASE)),
    ('vocatioal training', re.compile("veta|vocational training|chuo cha ufundi|technical training|vocation center|training college|training center|vocation centre|training centre", re.IGNORECASE)),
)


# Regex for school name
school_re = re.compile('school', re.IGNORECASE)


def clean_names(text):
    """Create a uniform pattern for school names"""
    new_text = text
    for p, r in names_mapping:
        new_text = p.sub(r, new_text)
    return new_text


if __name__ == '__main__':
    
    # Output directory
    op_directory = 'Schools/'
    if not os.path.exists(op_directory):
      os.makedirs(op_directory)

    # Clear the file used to store merged list of schools
    op_all = open(op_directory + 'schools.csv', 'w')
    op_all.write('')
    op_all.close()
    # Reopen file used to store merged list of schools
    op_all = open(op_directory + 'schools.csv', 'a')
    writer2 = csv.writer(op_all)

    # Loop through each input file
    for arg in sys.argv[1:]:
        #TODO: Add header row
        sys.stdout.write("\033[92m %s\033[0m\n  * Cleaning ...\n " %arg)
        # Output file for individual input file
        outpath = op_directory + arg
        # Temporary file
        outpath_tmp = op_directory + '.' + arg
        ip = open(arg, 'r')
        content = ip.read()
        out_content = clean_names(content)
        op_tmp = open(outpath_tmp, 'w')
        op_tmp.write(out_content)
        ip.close()
        op_tmp.close()
        
        sys.stdout.write(" * Categorizing ... \n")
        in_tmp = open(outpath_tmp, 'r')
        reader = csv.DictReader(in_tmp)
        op = open(outpath, 'w')
        writer = csv.writer(op)
        first_row = True
        for row in reader:
            try:
                name = row['School']
            except KeyError:
                try:
                   name = row['name'] 
                except KeyError:
                    name = row.pop('Particular', 'Unknown name')
            row['School'] = name
            if row.has_key('Village/Ar'):
                row['Village'] = row.pop('Village/Ar')
            # Fix cases where school names are placed under hamlet column
            if re.search(school_re, row.get('Hamlet', ''))\
                    and not re.search(school_re, row.get('School', '')):
                hamlet = row.get('School', '')
                school_name = row.get('Hamlet', '')
                name = row['School'] = school_name
                row['Hamlet'] = hamlet
            sorted_row = {}
            for key,value in sorted(row.items()):
                sorted_row [key] = value
            for c, p in categories_mapping:
                if re.search(p, name):
                    sorted_row['school_type'] = c
                    break
                else:
                    if not sorted_row.get('school_type'):
                        sorted_row['school_type'] = ''
            header_row = sorted_row.keys()
            if first_row:
                writer.writerow(header_row)
                first_row = False
            writer.writerow(sorted_row.values())
            writer2.writerow(sorted_row.values())
        op.close()
        os.remove(outpath_tmp)
    op_all.close()

    sys.stdout.write("""\n
        -----------------------------------------------------\n
        Output written to '\033[94m%s\033[0m' directory.\n
        -----------------------------------------------------\n"""
        % op_directory)
