import operate_db


def start():
    print('Welcome to Biojoin Basic')
    while True:  # keep looping until `break` statement is reached
        print("""Please select the action you want to proceed with:\n
                    1. Search in the database
                    2. Update the database
                    3. Delete from the database
                    4. General Info about the database
                    q. Quit 
                    """)
        tool_choice = input("Enter your choice: ").strip()
        if tool_choice not in ['1', '2', '3', '4', 'q']:
            print("Please choose one of the four actions by writing its corresponding number")
        else:
            break
    return tool_choice


def action(config, user_choice):
    # conn = operate_db.connect_db(config)
    conn = None
    if user_choice == '1':
        operate_db.pre_search(conn)
    elif user_choice == '2':
        operate_db.pre_update(conn)
    elif user_choice == '3':
        operate_db.pre_delete(conn)
    elif user_choice == '4':
        operate_db.info(conn)


def end():
    print("------------------")
    print("""Do you want to proceed?
            y - yes
            q - quit 
            """)
    answer = input()
    print("------------------")
    if answer == 'q':
        quit()


if __name__ == '__main__':
    CONFIGPATH = 'config.json'
    while True:
        user_selection = start()
        action(CONFIGPATH, user_selection)
        end()
