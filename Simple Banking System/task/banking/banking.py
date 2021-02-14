import random
import sqlite3 as db

# System states for user input
MAIN_MENU_CHOOSE = 1
ACCOUNT_MENU_CHOOSE = 2
LOGIN_INPUT = 3
TRANSFER_INPUT = 4
INCOME_INPUT = 5
EXITING = 10  # Technical final state for exit

# DB constants
DB_NAME = "card.s3db"
TABLE_NAME = "card"

# how many times system must try to generate card number that doesn't exist
CREATE_UNIQUE_CARD_NUM_MAX_TRIES = 5


class BankMachine:
    def __init__(self):
        self.db_conn = None
        self.state = MAIN_MENU_CHOOSE
        self.current_account = None

        self.login_question = None  # Additional state - counter for questions in LOGIN_INPUT state
        self.login_questions_buffer = {'card_num': "", 'pin_code': ""}

        self.transfer_question = None  # Additional state - counter for questions in TRANSFER_INPUT state
        self.transfer_questions_buffer = {'card_num': "", 'amount': ""}

    #################################
    #  Screens for the user input
    #################################

    def main_menu(self):
        print("\n1. Create an account")
        print("2. Log into account")
        print("0. Exit")

    def account_menu(self):
        print("\n1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")

    def ask_card_num(self):
        print("\nEnter your card number:")

    def ask_pin_code(self):
        print("Enter your PIN:")

    def ask_amount(self):
        print("\nEnter income:")

    def ask_transfer_card_num(self):
        print("\nTransfer\nEnter card number:")

    def ask_transfer_amount(self):
        print("Enter how much money you want to transfer:")

    #################################
    #  service functions
    #################################

    def check_sum_card_num(self, card_num_15):
        control_number = 0
        debug = ""
        for i, char in enumerate(card_num_15, 1):
            x = int(char)
            if i % 2:
                x *= 2
            if x > 9:
                x -= 9
            control_number += x
            debug = debug + str(x) + "+"
        rem = control_number % 10
        if rem != 0:
            return str(10 - rem)
        else:
            return '0'

    def clear_buffers(self):
        self.login_questions_buffer = {'card_num': "", 'pin_code': ""}
        self.transfer_questions_buffer = {'card_num': "", 'amount': ""}
        self.transfer_question = None
        self.login_question = None

    #################################
    #  Database layer
    #################################

    def db_check_connection(self):
        try:
            self.db_conn = db.connect(DB_NAME)
        except db.Error as e:
            print(e)
            self.state = EXITING
            return

        table_exists = self.db_conn.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}';").fetchone()

        if not table_exists:
            try:
                self.db_conn.execute(f"create table {TABLE_NAME} ("
                                     "      id      INTEGER PRIMARY KEY,"
                                     "      number  TEXT,"
                                     "      pin     TEXT,"
                                     "      balance INTEGER DEFAULT 0"
                                     ");")
                self.db_conn.commit()
            except db.Error as e:
                print(e)
                self.state = EXITING

    def db_get_card_balance(self, card_id):
        row = self.db_conn.execute(f"SELECT balance FROM {TABLE_NAME} where id = ? ;",
                                   (card_id,)).fetchone()
        if row:
            return row[0]

    def db_get_card_id_by_num(self, card_num):
        row = self.db_conn.execute(f"SELECT id FROM {TABLE_NAME} where number = ? ;",
                                   (card_num,)).fetchone()
        if row:
            return row[0]

    def db_insert_new_card(self, card_num, pin):
        try:
            cur = self.db_conn.execute(f"INSERT INTO {TABLE_NAME} (number, pin) VALUES (?,?)",
                                       (card_num, pin))
            self.db_conn.commit()
            return cur.lastrowid
        except db.Error as e:
            print(e)

    def db_get_card_by_num_and_pin(self, card_num, pin):
        row = self.db_conn.execute(
            f"SELECT id, number FROM {TABLE_NAME} where number = ? and pin = ? ;",
            (card_num, pin)).fetchone()
        if row:
            return {'id': row[0], 'card_num': row[1]}

    def db_delete_account(self, card_id):
        self.db_conn.execute(f"DELETE FROM {TABLE_NAME} where id = ? ;", (card_id, ))
        self.db_conn.commit()

    def db_increase_balance(self, card_id, amount):
        self.db_conn.execute(
            f"UPDATE {TABLE_NAME} SET balance = balance + ? where id = ? ;",
            (amount, card_id)).fetchone()

    #################################
    #  Commands implementation
    #################################

    def show_balance(self, account=None):
        if not account:
            account = self.current_account
        balance = self.db_get_card_balance(account['id'])
        print(f"\nBalance: {balance}")

    def create_account(self):
        random.seed()
        tries_count = 0

        while tries_count < CREATE_UNIQUE_CARD_NUM_MAX_TRIES:
            new_card_num = "400000"
            new_card_num += str(random.randint(0, 999999999)).rjust(9, '0')
            new_card_num += str(self.check_sum_card_num(new_card_num))
            pin_code = str(random.randint(0, 9999)).rjust(4, '0')

            if not self.db_get_card_id_by_num(new_card_num):
                new_id = self.db_insert_new_card(new_card_num, pin_code)
                if new_id:
                    print("\nYour card has been created")
                    print(f"Your card number:\n{new_card_num}")
                    print(f"Your card PIN:\n{pin_code}")
                    return
            tries_count += 1

    def add_income(self, income):
        self.db_increase_balance(self.current_account['id'], int(income))
        self.db_conn.commit()
        print("Income was added!")

    def load_account(self, log_info):
        account = self.db_get_card_by_num_and_pin(log_info['card_num'], log_info['pin_code'])
        if account:
            self.current_account = account
            print("\nYou have successfully logged in!")
            return account
        else:
            print("\nWrong card number or PIN!")

    def logout_account(self):
        self.current_account = None
        print("\nYou have successfully logged out!")

    def close_account(self):
        self.db_delete_account(self.current_account['id'])
        self.current_account = None
        print("\nThe account has been closed!")

    #################################
    #  Stateflow and processors
    #################################

    def process_account_action(self, line):
        if line == "0":
            self.state = EXITING
        elif line == "1":  # show balance
            self.show_balance()
        elif line == "2":  # add income
            self.state = INCOME_INPUT
        elif line == "3":  # Do transfer
            self.state = TRANSFER_INPUT
            self.clear_buffers()
            self.transfer_question = 0
        elif line == "4":  # close account
            self.close_account()
            self.state = MAIN_MENU_CHOOSE
        elif line == "5":  # logout
            self.logout_account()
            self.state = MAIN_MENU_CHOOSE

    def process_main_menu_action(self, line):
        if line == "0":
            self.state = EXITING
        elif line == "1":
            self.create_account()
        elif line == "2":
            self.state = LOGIN_INPUT
            self.clear_buffers()
            self.login_question = 0

    def process_login_input(self, line):
        if self.login_question == 0:
            self.login_question += 1
            self.login_questions_buffer['card_num'] = line

        elif self.login_question == 1:
            self.login_questions_buffer['pin_code'] = line

            if self.load_account(self.login_questions_buffer):
                self.state = ACCOUNT_MENU_CHOOSE
            else:
                self.state = MAIN_MENU_CHOOSE

            self.clear_buffers()
        else:
            pass

    def process_income_input(self, line):
        self.add_income(line)
        self.state = ACCOUNT_MENU_CHOOSE

    def process_transfer_input(self, line):
        if self.transfer_question == 0:
            if self.check_sum_card_num(line[:-1]) != line[-1:]:
                print("Probably you made a mistake in the card number. Please try again!")
                self.clear_buffers()
                self.state = ACCOUNT_MENU_CHOOSE
                return

            target_card_id = self.db_get_card_id_by_num(line)
            if not target_card_id:
                print("Such a card does not exist.")
                self.clear_buffers()
                self.state = ACCOUNT_MENU_CHOOSE
                return

            self.transfer_questions_buffer['card_num'] = line
            self.transfer_questions_buffer['target_card_id'] = target_card_id
            self.transfer_question += 1

        elif self.transfer_question == 1:
            balance = self.db_get_card_balance(self.current_account['id'])
            if int(line) > balance:
                print("Not enough money!")
            else:
                self.db_increase_balance(self.transfer_questions_buffer['target_card_id'], int(line))
                self.db_increase_balance(self.current_account['id'], -int(line))
                self.db_conn.commit()
                print("Success!")

            self.clear_buffers()
            self.state = ACCOUNT_MENU_CHOOSE
        else:
            pass

    def process_user_input(self, line):
        if self.state == MAIN_MENU_CHOOSE:
            self.process_main_menu_action(line)
        elif self.state == ACCOUNT_MENU_CHOOSE:
            self.process_account_action(line)
        elif self.state == LOGIN_INPUT:
            self.process_login_input(line)
        elif self.state == INCOME_INPUT:
            self.process_income_input(line)
        elif self.state == TRANSFER_INPUT:
            self.process_transfer_input(line)

    def show_input_screen(self):
        if self.state == MAIN_MENU_CHOOSE:
            self.main_menu()
        elif self.state == ACCOUNT_MENU_CHOOSE:
            self.account_menu()
        elif self.state == LOGIN_INPUT:
            if self.login_question == 0:
                self.ask_card_num()
            elif self.login_question == 1:
                self.ask_pin_code()
        elif self.state == INCOME_INPUT:
            self.ask_amount()
        elif self.state == TRANSFER_INPUT:
            if self.transfer_question == 0:
                self.ask_transfer_card_num()
            elif self.transfer_question == 1:
                self.ask_transfer_amount()

    def machine_run(self):
        self.db_check_connection()

        while self.state != EXITING:
            self.show_input_screen()
            line = input()
            self.process_user_input(line)

        print("\nBye!")
        if self.db_conn:
            self.db_conn.close()


bm = BankMachine()
#  print(bm.check_sum_card_num("400000735080216"))
# bm.db_check_connection()
# print(bm.db_conn.execute(f"SELECT * FROM {TABLE_NAME};").fetchall())

bm.machine_run()



