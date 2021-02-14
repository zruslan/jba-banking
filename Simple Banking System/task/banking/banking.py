import random
import sqlite3 as db

# Write your code here
MAIN_MENU_CHOOSE = 1
ACCOUNT_MENU_CHOOSE = 2
LOGIN_INPUT = 3
EXITING = 4  # Technical final state for exit

DB_NAME = "card.s3db"
TABLE_NAME = "card"


class BankMachine:
    def __init__(self):
        self.db_conn = None

        # self.accounts = {}
        self.state = MAIN_MENU_CHOOSE
        self.current_account = None

        self.login_question = None
        self.login_info_buffer = {'card_num': "", 'pin_code': ""}

    def main_menu(self):
        print("\n1. Create an account")
        print("2. Log into account")
        print("0. Exit")

    def account_menu(self):
        print("\n1. Balance")
        print("2. Log out")
        print("0. Exit")

    def ask_card_num(self):
        print("\nEnter your card number:")

    def ask_pin_code(self):
        print("Enter your PIN:")

    def show_balance(self, account=None):
        if not account:
            account = self.current_account
        print("\nBalance: {}".format(account['balance']))

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

    def try_insert_new_card(self, card_num, pin):
        row = self.db_conn.execute(f"SELECT * FROM {TABLE_NAME} where number = ? ;", (card_num,)).fetchone()
        if row:
            return
        else:
            try:
                cur = self.db_conn.execute(f"INSERT INTO {TABLE_NAME} (number, pin) VALUES (?,?)",
                                           (card_num, pin))
                self.db_conn.commit()
                return cur.lastrowid
            except db.Error as e:
                print(e)

    def create_account(self):
        random.seed()
        tries_count = 0

        while tries_count < 3:
            new_card_num = "400000"
            new_card_num += str(random.randint(0, 999999999)).rjust(9, '0')
            new_card_num += str(self.check_sum_card_num(new_card_num))
            pin_code = str(random.randint(0, 9999)).rjust(4, '0')

            new_id = self.try_insert_new_card(new_card_num, pin_code)
            if new_id:
                print("\nYour card has been created")
                print(f"Your card number:\n{new_card_num}")
                print(f"Your card PIN:\n{pin_code}")
                return
            tries_count += 1

    def clear_login_info_buffer(self):
        self.login_info_buffer = {'card_num': "", 'pin_code': ""}

    def logout_account(self):
        self.current_account = None
        self.clear_login_info_buffer()

#    def load_account(self, log_info):
#        if log_info['card_num'] in self.accounts:
#            account = self.accounts[log_info['card_num']]
#            if account['pin_code'] == log_info['pin_code']:
#                return account, "OK"
#        return None, "Wrong card number or PIN!"

    def load_account(self, log_info):
        cur = self.db_conn.execute(
                f"SELECT id, number, balance FROM {TABLE_NAME} where number = ? and pin = ? ;",
                    (log_info['card_num'],
                     log_info['pin_code']))
        row = cur.fetchone()
        if row:
            account = {'card_num': row[1],
                       'id': row[0],
                       'balance': row[2]}
            return account, "OK"
        return None, "Wrong card number or PIN!"

    def process_account_action(self, line):
        if line == "0":
            self.state = EXITING
        elif line == "1":
            self.show_balance()
        elif line == "2":
            self.logout_account()
            self.state = MAIN_MENU_CHOOSE
            print("\nYou have successfully logged out!")

    def process_main_menu_action(self, line):
        if line == "0":
            self.state = EXITING
        elif line == "1":
            self.create_account()
        elif line == "2":
            self.state = LOGIN_INPUT
            self.logout_account()
            self.login_question = 0

    def process_login_input(self, line):
        if self.login_question == 0:
            self.login_question += 1
            self.login_info_buffer['card_num'] = line
        elif self.login_question == 1:
            self.login_question = None
            self.login_info_buffer['pin_code'] = line

            account, mess = self.load_account(self.login_info_buffer)
            if account:
                self.current_account = account
                print("\nYou have successfully logged in!")
                self.state = ACCOUNT_MENU_CHOOSE
            else:
                print("\n" + mess)
                self.state = MAIN_MENU_CHOOSE
                self.clear_login_info_buffer()
        else:
            pass

    def show_screen(self):
        if self.state == MAIN_MENU_CHOOSE:
            self.main_menu()
        elif self.state == ACCOUNT_MENU_CHOOSE:
            self.account_menu()
        elif self.state == LOGIN_INPUT:
            if self.login_question == 0:
                self.ask_card_num()
            elif self.login_question == 1:
                self.ask_pin_code()

    def process_user_input(self, line):
        if self.state == MAIN_MENU_CHOOSE:
            self.process_main_menu_action(line)
        elif self.state == ACCOUNT_MENU_CHOOSE:
            self.process_account_action(line)
        elif self.state == LOGIN_INPUT:
            self.process_login_input(line)

    def check_connection(self):
        if self.db_conn:
            self.db_conn.close()

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
                                     "      id      INTEGER,"
                                     "      number  TEXT,"
                                     "      pin     TEXT,"
                                     "      balance INTEGER DEFAULT 0"
                                     ");")
                self.db_conn.commit()

            except db.Error as e:
                print(e)
                self.state = EXITING

    def machine_run(self):
        self.check_connection()

        while self.state != EXITING:
            self.show_screen()
            line = input()
            self.process_user_input(line)

        if self.db_conn:
            self.db_conn.close()


bm = BankMachine()
#  print(bm.check_sum_card_num("400000735080216"))
bm.machine_run()
