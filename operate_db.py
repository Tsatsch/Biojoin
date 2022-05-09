import template_sql as template_sql


def list_tables(db_connection):
    """ list available tables in db"""
    cur = db_connection.cursor()
    cur.execute("""SELECT table_name FROM information_schema.tables
           WHERE table_schema = 'public'""")
    return [value[0] for value in cur.fetchall()]


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
                            q. Quit
                            """)
            answer = input("Enter your choice: ").strip()
            if answer not in ['1', '2', '3', '4', 'q']:
                print("Please choose between 1, 2, 3, 4 and q")
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
