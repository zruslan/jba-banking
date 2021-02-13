import random

# Write your code here
MAIN_MENU_CHOOSE = 1
ACCOUNT_MENU_CHOOSE = 2
LOGIN_INPUT = 3
EXITING = 4  # Technical final state for exit


class BankMachine:
    def __init__(self):
        self.accounts = {}
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

    def create_account(self):
        random.seed()
        while True:
            new_card_num = "400000"
            new_card_num += str(random.randint(0, 999999999)).rjust(9, '0')
            new_card_num += str(self.check_sum_card_num(new_card_num))

            if new_card_num not in self.accounts:
                new_account = {'card_num': new_card_num,
                               'pin_code': str(random.randint(0, 9999)).rjust(4, '0'),
                               'balance': 0
                               }
                self.accounts[new_card_num] = new_account
                print("\nYour card has been created")
                print(f"Your card number:\n{new_card_num}")
                print(f"Your card PIN:\n{new_account['pin_code']}")
                return

    def clear_login_info_buffer(self):
        self.login_info_buffer = {'card_num': "", 'pin_code': ""}

    def logout_account(self):
        self.current_account = None
        self.clear_login_info_buffer()

    def load_account(self, log_info):
        if log_info['card_num'] in self.accounts:
            account = self.accounts[log_info['card_num']]
            if account['pin_code'] == log_info['pin_code']:
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

    def machine_run(self):
        while self.state != EXITING:
            self.show_screen()
            line = input()
            self.process_user_input(line)


bm = BankMachine()
#  print(bm.check_sum_card_num("400000735080216"))
bm.machine_run()

