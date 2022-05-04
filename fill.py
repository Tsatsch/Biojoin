import io
import json
import psycopg2
import pandas as pd


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


def parse_data(file):
    """
    :param file: TSV to parse
    :return: headers list and content list
    """

    csv_content = []

    with open(file) as f:
        headers = f.readline().strip().split("	")
        all_lines = f.readlines()
        for line in all_lines:
            csv_content.append(line.strip().split("	"))
    return headers, csv_content


def merge(file1_path, file2_path, merge_on):
    """we want to merge disease Omim and geneOmim"""
    file1 = pd.read_csv(file1_path, sep="	")
    file2 = pd.read_csv(file2_path, sep="	")
    return pd.merge(file1, file2, on=merge_on, how='outer')


def clean_csv_value(value):
    """ remove all non-visible \n in csv before inserting smth"""
    if value is None:
        return r'\N'
    return str(value).replace('\n', '\\n')


def fill_database(db_connection, table, headers, csv_content):
    cur = db_connection.cursor()
    # list of dictionaries with column names as keys and
    # value as row values
    q_args = []

    FROM = 0
    TILL = len(csv_content)

    for line in csv_content[FROM:TILL]:
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

    cur.close()
    db_connection.close()


if __name__ == '__main__':
    merged = merge('data/disease_OMIM.txt', 'data/gene_OMIM.txt', 'disease_OMIM_ID')
    merged.to_csv('data/merged.txt', sep="	", index=False)
    head1, cont1 = parse_data('data/Homo_sapiens_gene_info.txt')
    head2, cont2 = parse_data('data/SNP.txt')
    head3, cont3 = parse_data('data/merged.txt')

    conn = connect_db("config.json")
    fill_database(conn, "gene", head1, cont1)
    conn = connect_db("config.json")
    fill_database(conn, "dbsnp", head2, cont2)
    conn = connect_db("config.json")
    fill_database(conn, "omim", head3, cont3)
    print("Insert finished")
