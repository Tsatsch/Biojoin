import time

import template_sql as template_sql
import fill
import progressbar


def list_tables(db_connection):
    """ list available tables in db"""
    cur = db_connection.cursor()
    cur.execute("""SELECT table_name FROM information_schema.tables
           WHERE table_schema = 'public'""")
    return [value[0] for value in cur.fetchall()]


def get_table_size(db_connection, table_name):
    """ get number of rows in a given table"""
    cur = db_connection.cursor()
    query = f'SELECT count(*) FROM {table_name};'
    cur.execute(query)
    return cur.fetchone()[0]


def reset(db_connection):
    tables = list_tables(db_connection)
    cur = db_connection.cursor()
    # delete all tables
    if len(tables) > 0:
        querry = 'DROP table '
        for table in tables:
            querry += table + ", "
        querry = querry[:-2] + ";"
        cur.execute(querry)
        db_connection.commit()
    if len(list_tables(db_connection)) == 0:
        print("Tables deleted")

    # create new tables
    cur.execute(open("ddl.sql", "r").read())
    db_connection.commit()
    # fill db
    widgets = [
        '\x1b[33mCreation of new tables \x1b[39m',
        progressbar.Percentage(),
        progressbar.Bar(marker='\x1b[32m#\x1b[39m'),
    ]
    bar = progressbar.ProgressBar(widgets=widgets, max_value=5).start()
    counter = 0
    start = time.time()

    merged = fill.merge('data/disease_OMIM.txt', 'data/gene_OMIM.txt', "	", 'disease_OMIM_ID')
    merged.to_csv('data/merged.txt', sep="	", index=False)
    head1, cont1 = fill.parse_tsv('data/Homo_sapiens_gene_info.txt')
    fill.fill_database(db_connection, "gene", head1, cont1)
    counter += 1
    bar.update(counter)
    head2, cont2 = fill.parse_tsv('data/SNP.txt')
    fill.fill_database(db_connection, "snp", head2, cont2)
    counter += 1
    bar.update(counter)
    head3, cont3 = fill.parse_tsv('data/merged.txt')
    headers_disease = ['DiseaseName', 'DiseaseID', 'AltDiseaseIDs']
    cont4 = fill.parse_xml('data/CTD_diseases.xml', headers_disease)
    headers_disease_gene = ['DiseaseName', 'DiseaseID', 'AltDiseaseIDs', 'GeneSymb']
    disease_gene_content = fill.smart_merge_disease(disease_data=cont4, omim_data=cont3)
    fill.fill_database(db_connection, "disease", headers_disease_gene, disease_gene_content)
    counter += 1
    bar.update(counter)
    headers_chem_dis = ['ChemicalName', 'ChemicalID', 'DiseaseName', 'DiseaseID']
    cont6 = fill.parseCTO_tsv('data/CTD_chemicals_diseases.tsv')
    fill.fill_database(db_connection, "disease_drug", headers_chem_dis, cont6)
    counter += 1
    bar.update(counter)
    head7, cont7 = fill.generate_random_mock_toxicity(db_connection)
    fill.fill_database(db_connection, 'toxicity', head7, cont7)
    counter += 1
    bar.update(counter)
    head8, cont8 = fill.generate_random_mock_prevalence(db_connection)
    fill.fill_database(db_connection, 'prevalence', head8, cont8)

    end = time.time()
    bar.finish()
    print(f'Insert finished. It took {end - start} sec.')
    # make table_name: size
    table_size_str = ''
    for table in list_tables(db_connection):
        table_size_str += f'{table}: {get_table_size(db_connection, table)}' \
                          f' Rows\n'
    print(f'Available tables:\n{table_size_str}')


def cols_info(db_connection, table):
    """ get info about column names and
        their data types in a given table"""
    cur = None
    if table.strip() == "" or table is None:
        print("!!! No table name provided")
        quit()
    else:
        cur = db_connection.cursor()
        cur.execute(f'select column_name, data_type from information_schema.columns '
                    f'where table_name = \'{table}\';')
    res_dict = {}
    for tupl in cur.fetchall():
        res_dict[tupl[0]] = tupl[1]
    return res_dict


def pre_update(db_connection):
    """ collecting further data for update """
    print("*******************\n"
          "Update action...\n"
          "*******************")
    print(f'Available tables: {list_tables(db_connection)}')
    table = input("What table do you want to update in: ")
    while True:
        print("""What do you want to update?\n
                        a. Modify a row
                        b. Add a row
                        q. Quit
                        """)
        answer = input("Enter your choice: ").strip()
        if answer not in ['a', 'b', 'c', 'q']:
            print("Please choose between a, b, c or q")
        else:
            break

    cols_dic = cols_info(db_connection, table)
    if answer == 'a':
        print(f'Available cols: {list(cols_dic.keys())} ')
        condition = input("What do you want to modify? Please provide in SQL format: ")
        print("Please provide the new values")
        content = ""
        for colname, coltype in cols_dic.items():
            user_input = input(f'{colname}: ')
            if coltype == 'character varying' and \
                    "\'" not in user_input:
                user_input = f'\'{user_input}\''
            elif coltype == 'character varying' and \
                    '\"' in user_input:
                user_input = user_input.replace('\"', '')
                user_input = f'\'{user_input}\''
            content += f'{colname}={user_input}, '
        content = content[:-2]
        update(db_connection=db_connection, table=table, new_content=content,
               condition=condition, type_of_update='mod')
    elif answer == 'b':
        print(f'Available cols: {list(cols_dic.keys())} ')
        print("Please provide the new values")
        content = ""
        for colname, coltype in cols_dic.items():
            user_input = input(f'{colname}: ')
            if coltype == 'character varying' and \
                    "\'" not in user_input:
                user_input = f'\'{user_input}\''
            elif coltype == 'character varying' and \
                    '\"' in user_input:
                user_input = user_input.replace('\"', '')
                user_input = f'\'{user_input}\''
            content += f'{user_input}, '
        content = content[:-2]
        update(db_connection=db_connection, table=table,
               new_content=content, type_of_update='add_r')
    else:
        quit()


def update(db_connection, table, new_content, type_of_update, condition=None):
    query = None
    if type_of_update == 'mod':
        query = f'UPDATE {table} SET {new_content} WHERE {condition}'
        print(f'UPDATE {table} SET {new_content} WHERE {condition}')
    elif type_of_update == 'add_r':
        query = f'INSERT INTO {table} VALUES ({new_content});'
    else:
        raise ValueError("Wrong type of update")

    cur = db_connection.cursor()
    cur.execute(query)
    db_connection.commit()
    print("Table was updated")


def pre_delete(db_connection):
    """ collecting further data for deletion """
    print("*******************\n"
          "Delete action...\n"
          "*******************")
    while True:
        print("""Do you want to delete table or entry in table?\n
                        a. Entry in table
                        b. Whole table 
                        q. Quit
                        """)
        answer = input("Enter your choice: ").strip()
        if answer not in ['a', 'b', 'q']:
            print("Please choose between a, b or q")
        else:
            break

    if answer == 'a':
        print(f'Available tables: {list_tables(db_connection)}')
        table = input("What table do you want to delete in: ")
        print(f'Available cols: {list(cols_info(db_connection, table).keys())}')
        cond = input("What do you want to search? Please provide in SQL format: ")
        print(f'Deleting in {table} with condition\n{cond}')
        delete(db_connection, table, cond)
    elif answer == 'b':
        print(f'Available tables: {list_tables(db_connection)}')
        table = input("What table do you want to delete: ")
        print(f'Deleting table {table}')
        delete_table(db_connection, table)
    else:
        quit()


def delete_table(db_connection, table):
    cur = db_connection.cursor()
    query = ""
    if table.strip() == "" or table is None:
        print("!!! No table name provided")
        quit()
    else:
        query = f'DROP TABLE IF EXISTS {table};'
    cur.execute(query)
    db_connection.commit()

    print(f'Table {table} was deleted')


def delete(db_connection, table, condition):
    cur = db_connection.cursor()
    if (table.strip() == "" or table is None) or \
            (condition.strip() == "" or condition is None):
        print("!!! No table name provided")
        quit()
    else:
        query = f'DELETE FROM {table} WHERE {condition};'
        cur.execute(query)
        db_connection.commit()

    print("An entry in table was deleted")


def pre_search(db_connection):
    """ collecting further data for search """
    print("*******************\n"
          "Search action...\n"
          "*******************")
    print(f'Available tables: {list_tables(db_connection)}')
    while True:
        print("""Pick option?\n
                        a. Try out the search templates
                        b. Make own search query
                        q. Quit
                        """)
        answer = input("Enter your choice: ").strip()
        if answer not in ['a', 'b', 'q']:
            print("Please choose between a, b or q")
        else:
            break
    if answer == 'a':
        while True:
            print("""What template do you want to try out?\n
                            1. Find all gene information
                            2. Find all gene symbols located in the chromosome
                            3. Find all diseases associated with the SNP
                            4. Find all SNP IDs associated with the disease
                            5. Find drug to treat given disease
                            6. Find diseases that can be treated with your drug
                            7. Find genes that are affected by given drug
                            q. Quit
                            """)
            answer = input("Enter your choice: ").strip()
            if answer not in ['1', '2', '3', '4', '5', '6', '7', 'q']:
                print("Please choose between 1, 2, 3, 4, 5, 6, 7 and q")
            else:
                break

        if answer == '1':
            answer2 = input("Please provide a gene symbol: ")
            print(template_sql.get_gene_info(db_connection, answer2)[0])
        elif answer == '2':
            answer2 = input("Please provide a chromosome number: ")
            res = template_sql.get_genes_on_chromosome(db_connection, answer2)
            print([value[0] for value in res])
        elif answer == '3':
            answer2 = input("Please provide a SNP id: ")
            res = template_sql.find_diseases(db_connection, answer2)
            print([value[0] for value in res])
        elif answer == '4':
            answer2 = input("Please provide a disease name: ")
            res = template_sql.find_snp(db_connection, answer2)
            print([value[0] for value in res])
        elif answer == '5':
            answer2 = input("Please provide a disease name: ")
            res = template_sql.get_drugs(db_connection, answer2)
            print(res)
        elif answer == '6':
            answer2 = input("Please provide a drug name: ")
            res = template_sql.get_diseases(db_connection, answer2)
            print(res)
        elif answer == '7':
            answer2 = input("Please provide a drug name: ")
            res = template_sql.get_genes_from_drug(db_connection, answer2)
            print(res)
        else:
            quit()

    if answer == 'b':
        table = input("What table do you want to search in: ")
        cols_dic = cols_info(db_connection, table)
        print(f'Available cols: {list(cols_dic.keys())}')
        cond = input("What do you want to search? Please provide in SQL format: ")
        res = search(db_connection, table, cond)
        return res
    else:
        quit()


def search(db_connection, table, condition):
    cur = db_connection.cursor()
    # get tables columns names
    query = ""
    if table.strip() == "" or table is None:
        print("!!! No table name provided")
        quit()
    elif condition.strip() == "" or condition is None:
        query = f'SELECT * FROM {table}'
    else:
        query = f'SELECT * FROM {table} WHERE {condition};'

    cur.execute(query)
    result = [value for value in cur.fetchall()]
    db_connection.commit()

    return result
