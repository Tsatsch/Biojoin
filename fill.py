import io
import json
import xml.etree.ElementTree as et

from random import random
from random import randrange

import psycopg2
import pandas as pd
import csv


def connect_db(config_path):
    """ Connect to the PostgreSQL database server
        with given config """

    with open(config_path) as f:
        config = json.load(f)

    connection = None
    try:
        connection = psycopg2.connect(
            host=config["db_host"],
            dbname=config["db_name"],
            user=config["db_user"],
            password=config["db_pw"])
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return connection


def parseCTO_tsv(file):
    """
        :param file: TSV to parse
        :return: headers list and content list
        for now a bit hard-coded headers, needs to be fixed later
        """
    content = []
    with open(file) as f:
        all_data = f.readlines()
        for line in all_data:
            if not line.startswith("#"):
                single_row_splitted = line.strip().split('	')
                single_row_filtered = [single_row_splitted[0], single_row_splitted[1],
                                       single_row_splitted[3], single_row_splitted[4]]
                content.append(single_row_filtered)

    # remove duplicates
    dup_free = []
    dup_free_set = set()
    for x in content:
        if tuple(x) not in dup_free_set:
            dup_free.append(x)
            dup_free_set.add(tuple(x))

    return dup_free


def parse_tsv(file):
    """
    :param file: TSV to parse
    :return: headers list and content list
    """

    content = []

    with open(file) as f:
        head = f.readline().strip().split("	")
        all_lines = f.readlines()
        for line in all_lines:
            content.append(line.strip().split("	"))
    return head, content


def parse_xml(file, heads):
    """
    :param file: xml to parse
    :param headers: XML tags/headers to consider only
    :return: headers list and content list
    """
    root_node = et.parse(file).getroot()
    xml_content = []
    # find longest xml element to get all possible headers
    for entry in root_node:
        single_row = []
        for el in entry:
            if el.tag in heads:
                single_row.append(el.text)
        if len(single_row) < len(heads):  # if no alt_symb
            single_row.append(None)
        xml_content.append(single_row)

    return xml_content


def generate_random_values_columns(file_path, name_of_new_col):
    with open(file_path) as f:
        header = f.readline().strip().split('	')
        reader = csv.reader(f, delimiter='	')
        data = list(reader)

    new_data = []
    for value in data:
        random_popularity = round(random() * 100, 2)
        new_row = value
        new_row.append(random_popularity)
        new_data.append(new_row)

    header.append(name_of_new_col)
    new_file_path = file_path.split(".")[0]+"_random.txt"
    with open(new_file_path, 'w') as f:
        writer = csv.writer(f, delimiter='	')
        writer.writerow(header)
        writer.writerows(new_data)
    return new_file_path

def merge(file1_path, file2_path, file_separator, merge_on):
    """we want to merge disease Omim and geneOmim"""
    file1 = pd.read_csv(file1_path, sep=file_separator)
    file2 = pd.read_csv(file2_path, sep=file_separator)
    return pd.merge(file1, file2, on=merge_on, how='outer')


def smart_merge_disease(disease_data, omim_data):
    """ from CTD diseases we obtain the OMIM id and 
        from OMIM get the gene_sysmb to add to CTD diseses
    :param content: insertion of 2d lists of content
    :return: headers list and content list of merged datastrcutre   
    """
    full_disease_data = []
    for disease in disease_data:
        # if omim is in id (isted of mesh)
        if 'OMIM' in disease[1]:
            disease_omim_id = disease[1].split(':')[1]
            for omim in omim_data:
                if omim[0] == disease_omim_id:
                    full_single_disease = disease.copy()
                    full_single_disease.append(omim[2])
                    full_disease_data.append(full_single_disease)

        omim_alternatives = None
        # if omim in alternative ids
        if disease[2] is not None:
            alternatives = disease[2].split("|")
            omim_alternatives = [omim.split(':')[1] for omim in alternatives if 'OMIM:' in omim]
            if len(omim_alternatives) > 0:
                for omim in omim_data:
                    if omim[0] in omim_alternatives:
                        full_single_disease = disease.copy()
                        full_single_disease.append(omim[2])
                        full_disease_data.append(full_single_disease)
        else:
            # no omim in id or alternative ids
            # here we had an issue that on one side we can have same OMIM or MESH but different Gene symbols, so disease_id (OMIM or Mesh) + genesymbol 
            # should be both primary keys to avoid it
            # on the other hand, sometimes we dont have omim at all (neither in disease_id nor in alternatives), so for some entries genesymbol is None which 
            # violates not-null constraint of primary key, so we cannot make both disease id and gene symbol PK
            # what to do?
            # - mock value of gene id e.g. 'NONE'
            single_disease_no_omim = disease.copy()
            single_disease_no_omim.append('None')
            full_disease_data.append(single_disease_no_omim)

            # remove duplicated entries (can happen if different omims point at same gene
    # from https://blog.finxter.com/how-to-remove-duplicates-from-a-python-list-of-lists/
    dup_free_full_disease_data = []
    dup_free_set = set()
    for x in full_disease_data:
        if tuple(x) not in dup_free_set:
            dup_free_full_disease_data.append(x)
            dup_free_set.add(tuple(x))

    return dup_free_full_disease_data


def generate_random_mock_toxicity(db_connection):
    """assigns a random toxicity percentage (0-100) to a drug"""
    cur = db_connection.cursor()
    cur.execute("""select drug_id from disease_drug;""")
    all_drugs_ids = list(set([tupl[0] for tupl in cur.fetchall()]))

    headers = ['drug_id', 'tox']
    data = []
    for drug in all_drugs_ids:
        random_tox_percent = round(random() * 100, 2)
        data.append([drug, random_tox_percent])

    return headers, data


def generate_random_mock_prevalence(db_connection):
    """assigns a random Prevalence to a disease"""
    cur = db_connection.cursor()
    cur.execute("""select disease_id from disease_drug;""")
    all_diseases_ids = list(set([tupl[0] for tupl in cur.fetchall()]))

    headers = ['disease_id', 'prevalence']
    data = []
    for disease in all_diseases_ids:
        random_tox_percent = randrange(1000, 10 ** 6)
        data.append([disease, random_tox_percent])

    return headers, data


def clean_csv_value(value):
    """ remove all non-visible \n in csv before inserting smth"""
    if value is None:
        return r'\N'
    return str(value).replace('\n', '\\n')


def fill_database(db_connection, table, headers, data):
    cur = db_connection.cursor()
    # list of dictionaries with column names as keys and
    # value as row values
    q_args = []

    FROM = 0
    TILL = len(data)

    for line in data[FROM:TILL]:
        q_dict_arg = {}
        for key, value in zip(headers, line):
            q_dict_arg[key] = value

        q_args.append(q_dict_arg)

    # make a object csv and copy into db for best performance
    # see: copy_stringio() from https://hakibenita.com/fast-load-data-python-postgresql
    csv_file_like_object = io.StringIO()

    for arg in q_args:
        csv_file_like_object.write('~'.join(map(clean_csv_value, arg.values())) + '\n')

    csv_file_like_object.seek(0)
    cur.copy_from(csv_file_like_object, f'{table}', sep='~')
    # commit request
    db_connection.commit()
