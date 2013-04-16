"Unit tests for ledger.py"

from ledger import chart_of_accounts, print_accounts, parse_amount, \
                   root_account_name, is_valid_account_string, is_balanced, \
                   account_string_components, account_tree_from_account_strings, \
                   account_string_and_parents, balance_amounts, contains_account, \
                   join_columns, justify_columns \

def test_join_columns():
    assert join_columns([['a','b'], ['c','d']])==['a b', 'c d']

def test_justify_columns():
    assert justify_columns([['aaaa','b'], ['c','ddd']], "LR") == [['aaaa', '  b'], ['c   ', 'ddd']]
    assert justify_columns([['aaaa','b'], ['c','ddd']], "RL") == [['aaaa', 'b  '], ['   c', 'ddd']]
    assert justify_columns([], "RL") == []

def test_parse_amount():
    assert parse_amount('-$285.21') == {'units': 'AUD', 'quantity': -28521}
    assert parse_amount('$2,073.68') == {'units': 'AUD', 'quantity': 207368}


def test_root_account_name():
    assert root_account_name("Equity:Matthew") == "EQUITY"
    assert root_account_name("Assets:Cash") == "ASSETS"
    ## Convert asset/liability/expense to plural.
    assert root_account_name("Asset:Cash") == "ASSETS"
    assert root_account_name("liability") == "LIABILITIES"
    assert root_account_name("expense") == "EXPENSES"

def test_is_valid_account_string():
    ## Account strings are ':' delimited
    assert is_valid_account_string("assets.matthew") == False
    assert is_valid_account_string("assets:matthew") == True


def test_is_balanced():
    transaction_wrong = {'date': '2013-02-28', 'description': 'Opening Balance Bankwest Telenet Saver.',
                         'postings': [{'account': 'Assets:Bank:Westpac:123456',
                                       'amount': {'units': 'AUD', 'quantity': 22863}},
                                      {'account': 'Equity:OpeningBalances',
                                       'amount': {'units': 'AUD', 'quantity': -22863}}]}
    assert is_balanced(transaction_wrong) == False
    transaction_right = {'date': '2013-02-28', 'description': 'Opening Balance Bankwest Telenet Saver.',
                         'postings': [{'account': 'Assets:Bank:Westpac:123456',
                                    'amount': {'units': 'AUD', 'quantity': 22863}},
                                      {'account': 'Equity:OpeningBalances',
                                    'amount': {'units': 'AUD', 'quantity': 22863}}]}
    assert is_balanced(transaction_right) == True

def test_account_analysis():
    assert account_string_components('equity:foo') == {'original': ['equity', 'foo'],
                                                       'regular': ['EQUITY', 'FOO']}

class TestAccounts:
    def setUp(self):
        self.account_strings = ["Expenses:Birthdays:Angus",
                                "Expenses:Birthdays:Saskia",
                                "Income:Wages:RBS",
                                "Income:Investment:Shares:Dividends",
                                "Income:Investment:Shares:CapitalGains",
                                "Income:Interest",
                                "Equity"]

        self.chart_of_accounts = ['Equity',
                                  'Expenses:Birthdays',
                                  '  Angus',
                                  '  Saskia',
                                  'Income',
                                  '  Interest',
                                  '  Investment:Shares',
                                  '    CapitalGains',
                                  '    Dividends',
                                  '  Wages:RBS']

        self.account_structure = {'INCOME': {'has_own_postings': False,
                                             'balances': {},
                                             'name': 'Income',
                                             'sub_accounts': {
                                                 'WAGES': {'has_own_postings': False,
                                                           'balances': {},
                                                           'name': 'Wages',
                                                           'sub_accounts': {
                                                               'RBS': {'has_own_postings': True,
                                                                       'balances': {},
                                                                       'name': 'RBS',
                                                                       'sub_accounts': {}}}},
                                                 'INVESTMENT': {'has_own_postings': False,
                                                                'balances': {},
                                                                'name': 'Investment',
                                                                'sub_accounts': {
                                                                    'SHARES': {'has_own_postings': False,
                                                                               'balances': {},
                                                                               'name': 'Shares',
                                                                               'sub_accounts': {
                                                                                   'DIVIDENDS': {'has_own_postings': True,
                                                                                                 'balances': {},
                                                                                                 'name': 'Dividends',
                                                                                                 'sub_accounts': {}},
                                                                                   'CAPITALGAINS': {'has_own_postings': True,
                                                                                                    'balances': {},
                                                                                                    'name': 'CapitalGains',
                                                                                                    'sub_accounts': {}}}}}},
                                                 'INTEREST': {'has_own_postings': True,
                                                              'balances': {},
                                                              'name': 'Interest',
                                                              'sub_accounts': {}}}},
                                  'EQUITY': {'has_own_postings': True,
                                             'balances': {},
                                             'name': 'Equity',
                                             'sub_accounts': {}},
                                  'EXPENSES': {'has_own_postings': False,
                                               'balances': {},
                                               'name': 'Expenses',
                                               'sub_accounts': {
                                                   'BIRTHDAYS': {'has_own_postings': False,
                                                                 'balances': {},
                                                                 'name': 'Birthdays',
                                                                 'sub_accounts': {
                                                                     'ANGUS': {'has_own_postings': True,
                                                                               'balances': {},
                                                                               'name': 'Angus',
                                                                               'sub_accounts': {}},
                                                                     'SASKIA': {'has_own_postings': True,
                                                                                'balances': {},
                                                                                'name': 'Saskia',
                                                                                'sub_accounts': {}}}}}}}



    def test_account_tree_from_account_strings(self):
        assert account_tree_from_account_strings(self.account_strings) == self.account_structure

    def test_chart_of_accounts(self):
        "Check account hierarchy is represented correctly in text."
        assert chart_of_accounts(account_tree_from_account_strings(self.account_strings)) == self.chart_of_accounts

def test_account_string_and_parents():
    assert account_string_and_parents('expenses:charity:Sponsorship:40HrFamine') == ['EXPENSES',
                                                                              'EXPENSES:CHARITY',
                                                                              'EXPENSES:CHARITY:SPONSORSHIP',
                                                                              'EXPENSES:CHARITY:SPONSORSHIP:40HRFAMINE']
def test_balance_amounts():
    transaction = {'date': '2013-02-28', 'line': 1, 'description': 'Opening Balance',
                   'postings': [{'amount': {'units': 'AUD',
                                            'quantity': 1234},
                                 'account': 'Assets:Cash'},
                                {'amount': {'units': 'AUD',
                                            'quantity':  1234},
                                 'account': 'Equity:OpeningBalances'}]}

    assert balance_amounts(transaction) == [{'units': 'AUD', 'quantity': 0}]

def test_contains_account():
    assert contains_account("Income", "Expenses:Phone") == False
    assert contains_account("Income", "Income:Salary") == True
