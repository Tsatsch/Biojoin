import psycopg2
from fill import connect_db


def pre_update(db_connection):
    """ collecting further data for update """
    print("Update action")
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

        if answer == 'a':
            cond = input("What do you want to update? Please provide in SQL format: ")
            content = input("Please specify the new content in SQL format:  ")
            update(db_connection, table, cond, content, 'mod')
        elif answer == 'b':
            content = input("Please provide the new values in SQL format:  ")
            update(db_connection, table, None, content, 'add_r')
        else:
            quit()


def update(db_connection, table, condition, new_content, type_of_update):
    if type_of_update == 'mod':
        pass
    elif type_of_update == 'add_r':
        pass
    elif type_of_update == 'add_c':
        pass
    else:
        raise ValueError("Wrong type of update")

    # cur = db_connection.cursor()
    # get tables columns names
    query = f'ALTER TABLE {table} ADD COLUMN ...;'


    # query = "ALTER TABLE mytable ADD COLUMN sid serial PRIMARY KEY"

    # cur.execute(query)
    #
    # db_connection.commit()
    # cur.close()
    # db_connection.close()
    print("Table was updated")


def pre_delete(db_connection):
    """ collecting further data for deletion """
    print("Deleting action")
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
        table = input("What table do you want to delete in: ")
        cond = input("What do you want to search? Please provide in SQL format: ")
        print(f'Deleting in {table} with condition\n{cond}')
        delete(db_connection, table, cond)
    elif answer == 'b':
        table = input("What table do you want to delete: ")
        print(f'Deleting table {table}')
        delete_table(db_connection, table)
    else:
        quit()


def delete_table(db_connection, table):
    # cur = db_connection.cursor()
    # get tables columns names
    query = f'DROP TABLE IF EXISTS {table};'

    # cur.execute(query)
    # db_connection.commit()
    # cur.close()
    # db_connection.close()

    print(f'Table {table} was deleted')


def delete(db_connection, table, condition):
    # cur = db_connection.cursor()
    # get tables columns names
    query = f'DELETE FROM {table} WHERE {condition};'

    # cur.execute(query)
    # db_connection.commit()
    # cur.close()
    # db_connection.close()

    print("An entry in table was deleted")


def pre_search(db_connection):
    """ collecting further data for search """
    print("Searching action")
    table = input("What table do you want to search in: ")
    cond = input("What do you want to search? Please provide in SQL format: ")
    print(f'Searching in {table} with condition\n{cond}')
    res = search(db_connection, table, cond)


def search(db_connection, table, condition):
    # cur = db_connection.cursor()
    # get tables columns names
    query = f'SELECT * FROM {table} WHERE {condition};'
    # result = [value[0] for value in cur.fetchall()]

    # cur.execute(query)
    # db_connection.commit()
    # cur.close()
    # db_connection.close()
    print("Search result")


def info(db_connection):
    # cur = db_connection.cursor()
    query = "SELECT * FROM information_schema.tables;"
    # cur.execute(query)
    # result = [value[0] for value in cur.fetchall()]
    # print(res)
    # db_connection.commit()
    # cur.close()
    # db_connection.close()
    print("Info")