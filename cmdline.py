import fill
import operate_db


def start():
    print('Welcome to Biojoin Basic')
    while True:  # keep looping until `break` statement is reached
        print("""Please select the action you want to proceed with:\n
                    1. Search in the database
                    2. Update the database
                    3. Delete from the database
                    rr. reset or/and setup new database
                    q. Quit 
                    """)
        tool_choice = input("Enter your choice: ").strip()
        if tool_choice not in ['1', '2', '3', 'q', 'rr']:
            print("Please choose one of the four actions by writing "
                  "its corresponding number")
        else:
            break
    return tool_choice


def action(config, user_choice):
    conn = fill.connect_db(config)
    if user_choice == '1':
        res = operate_db.pre_search(conn)
        print(res)
    elif user_choice == '2':
        operate_db.pre_update(conn)
    elif user_choice == '3':
        operate_db.pre_delete(conn)
    elif user_choice == 'rr':
        confirm_reset(conn)


def confirm_reset(conn):
    # make table_name: size
    table_size_str = ''
    for table in operate_db.list_tables(conn):
        table_size_str += f'{table}: {operate_db.get_table_size(conn, table)}' \
                          f' Rows\n'

    print("------------------")
    print(f'Are you sure you want to delete all current tables and create new ones?\n'
          f'Tables to be deleted:\n{table_size_str}\n'
          f'y - yes\n'
          f'n, q - no, quit\n')
    answer = input('Answer: ')
    print(answer)
    print("------------------")
    if answer == 'n' or answer == 'q' or answer == '':
        quit()
    if answer == 'y':
        operate_db.reset(conn)


def end():
    print("------------------")
    print("""Do you want to continue?
            y - yes
            n, q - no, quit
            """)
    answer = input('Answer: ')
    print("------------------")
    if answer == 'n' or answer == 'q' or answer == '':
        quit()


if __name__ == '__main__':
    CONFIGPATH = 'config.json'
    while True:
        user_selection = start()
        action(CONFIGPATH, user_selection)
        end()
