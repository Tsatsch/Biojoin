import fill
import operate_db


def start():
    print('Welcome to Biojoin Basic')
    while True:  # keep looping until `break` statement is reached
        print("""Please select the action you want to proceed with:\n
                    1. Search in the database
                    2. Update the database
                    3. Delete from the database
                    q. Quit 
                    rr. reset or/and setup new database
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
        operate_db.reset(conn)


def end():
    print("------------------")
    print("""Do you want to continue?
            y - yes
            n, q - no, quit
            """)
    answer = input()
    print("------------------")
    if answer == 'n' or answer == 'q':
        quit()


if __name__ == '__main__':
    CONFIGPATH = 'config.json'
    while True:
        user_selection = start()
        action(CONFIGPATH, user_selection)
        end()
