#!/usr/bin/env python

# This file is part of ledger-py.
#
# ledger-py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ledger-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ledger-py.  If not, see <http://www.gnu.org/licenses/>.

"""Command-line, double-entry accounting in python.

Inspired by John Wiegley's Ledger:
  http://www.ledger-cli.org/
"""

import argparse
import sys
import dateutil.parser
from collections import defaultdict

# {{{ Deal with columns of text

def join_columns(seq_of_seq_of_strings, separator=' '):
    result = []
    for row in seq_of_seq_of_strings:
        result += [separator.join(row)]
    return result

def justify_columns(seq_of_seq_of_strings, justification):
    """Justify strings in sequence of sequences so each column has equal length.

    Characters in justification indicate left ('L') or right ('R')
    justification. Anything beside l/r/L/R isn't justified.

    Take a sequence of sequences of strings. Make sure strings in nth
    position of inner sequence are same length by right-justifying
    them.

    Assumes each inner sequence has same # of components."""

    ## XXX: *just_col* need rewriting to remove duplicate code
    if (len(seq_of_seq_of_strings) == 0):
        return seq_of_seq_of_strings
    for column in range(len(justification)):
        if justification[column].upper() == "L":
            seq_of_seq_of_strings = ljust_column(seq_of_seq_of_strings, column)
        if justification[column].upper() == "R":
            seq_of_seq_of_strings = rjust_column(seq_of_seq_of_strings, column)
    return seq_of_seq_of_strings

def rjust_column(seq_of_seq_of_strings, column):
    """Right-justify strings in sequence of sequences so all values in column have equal length.

    Take a sequence of sequences of strings. Make sure strings in nth
    position of inner sequences are same length by right-justifying
    them.

    Assumes each inner sequence has same # of components."""

    ## XXX: ljust_col*, rjust_col* need rewriting to remove duplicate code
    if (len(seq_of_seq_of_strings) == 0):
        return seq_of_seq_of_strings
    # else
    ## Make copy where inner sequences are lists, so we can modify them
    seq_of_seq_of_strings = [list(row) for row in seq_of_seq_of_strings]
    max_len = max([len(row[column]) for row in seq_of_seq_of_strings])
    for row in range(len(seq_of_seq_of_strings)):
        seq_of_seq_of_strings[row][column] = seq_of_seq_of_strings[row][column].rjust(max_len)
    return seq_of_seq_of_strings

def ljust_column(seq_of_seq_of_strings, column):
    """Left-justify strings in sequence of sequences so all values in column have equal length.

    Take a sequence of sequences of strings. Make sure strings in nth
    position of inner sequences are same length by left-justifying
    them.

    Assumes each inner sequence has same # of components."""

    ## XXX: ljust_col*, rjust_col* need rewriting to remove duplicate code
    if (len(seq_of_seq_of_strings) == 0):
        return seq_of_seq_of_strings
    # else
    ## Make copy where inner sequences are lists, so we can modify them
    seq_of_seq_of_strings = [list(row) for row in seq_of_seq_of_strings]
    max_len = max([len(row[column]) for row in seq_of_seq_of_strings])
    for row in range(len(seq_of_seq_of_strings)):
        seq_of_seq_of_strings[row][column] = seq_of_seq_of_strings[row][column].ljust(max_len)
    return seq_of_seq_of_strings


# }}}

# {{{ Units / Currencies

### XXX: This code isn't good for anything besides AUD at the moment.
### Maybe not even good for AUD. Should really be using a the decimal
### module for this.

DEFAULT_UNITS = 'AUD'

def parse_amount(amount_string):
    "Convert amount_string to a unit/currency and signed quantity."

    # Special case for no unit/ccy
    if amount_string == "-":
        return {}

    quantity = int(round(float(amount_string.translate(None, "$,")) * 100.0))

    return {'units': 'AUD',
            'quantity': quantity}

def parse_amount_adjusting_sign(account_string, amount_string):
    "Parse amount_string, adjust sign depending on account_string."

    quantity = int(round(float(amount_string.translate(None, "$,")) * 100.0))
    quantity *= sign_account(account_string)

    return {'units': 'AUD',
            'quantity': quantity}

def format_amount(amount):
    "Format unit/currency quantity as a string."

    # Special format for nothing at all
    if amount == {}:
        return "-"

    units = amount['units']
    quantity = amount['quantity']

    if units == 'AUD':
        if quantity >= 0:
            return "${0:,.2f}".format(quantity/100.0)
        else:
            return "-${0:,.2f}".format(-quantity/100.0)
    #else:
    raise Exception('Unknown unit in format_amount:', units)

def extract_single_unit_amount(amounts):
    "Given a set of amounts, make sure there is exactly one currency/unit present and return that amount."
    if len(amounts.keys()) == 1:
        return amounts.values()[0]
    # else
    raise ValueError("extract_single_unit_amount: amounts do not contain a single unit/ccy:", amounts)

def extract_nil_or_single_unit_amount(amounts):
    "Given a set of amounts, make sure there is zero or one currency/unit present and return that amount."
    if len(amounts.keys()) == 1:
        return amounts.values()[0]
    elif (amounts == {}):
        return amounts
    # else
    raise ValueError("extract_nil_or_single_unit_amount: amounts contain >1 unit/ccy:", amounts)

def format_single_unit_amount(amounts):
    "Given a set of amounts, make sure there is exactly one currency/unit present and return that amount."
    return format_amount(extract_single_unit_amount(amounts))

def format_nil_or_single_unit_amount(amounts):
    "Given a set of amounts, make sure there is zero or one currency/unit present and return that amount."
    return format_amount(extract_nil_or_single_unit_amount(amounts))

def difference_nil_or_single_unit_amount(amount1, amount2):
    "Return amount1 - amount 2 with units of same ccy."
    if amount1 == {}:
        return amount2
    if amount2 == {}:
        return amount1
    if (amount1['units'] <> amount2['units']):
        raise ValueError("difference_nil_or_single_unit_amount: different units in amount1 and amount2:", amount1, amount2)
    return {'units': amount1['units'],
            'quantity': amount1['quantity'] - amount2['quantity']}


# }}}

def root_account_name(account_string):
    """Return regularised version of root account's name'.

    Basically, we convert to upper case, but we also make sure that
    root name is a plural if the singular was used instead. We also
    treat 'revenue' or 'revenues' accounts as 'income' accounts."""
    root = account_string.split(':')[0]
    root = root.upper()
    if (root == "EXPENSE"):
        return "EXPENSES"
    if (root == "ASSET"):
        return "ASSETS"
    if (root == "LIABILITY"):
        return "LIABILITIES"
    if (root == "REVENUE"):
        return "INCOME"
    if (root == "REVENUES"):
        return "INCOME"
    return root

def sign_account(account_string):
    """Do debits increase or decrease the account?

    This is a simplified way of checking that debits and credits in a
    transaction balance. For the unsimplified version, see:

      http://en.wikipedia.org/wiki/Debits_and_credits

    All we really need to do is work out whether or not postings in a
    transaction balance in a double-entry bookkeeping sense. Instead
    of using 'debit' and 'credit' amounts, we let postings change
    accounts by a positive or negative amounts, and test that the
    postings in a transaction balance by checking that they sum to
    zero after their amounts are converted using a using a sign that
    depends on the account.

    For example the postings:

      Assets: +1, Income: +1

    balance since the 'Assets' and 'Income' accounts have opposite signs
    (+1, and -1) here. Similarly, the postings:

      Assets: -1, Expenses: +1

    balance because the Assets and Expenses accounts have the same
    signs (+1, and +1)."""

    account_sign_dict = {'ASSETS': 1,
                         'LIABILITIES' : -1,
                         'INCOME' : -1,
                         'EXPENSES' : 1,
                         'EQUITY': -1}
    return account_sign_dict[root_account_name(account_string)]

def is_valid_account_string(account_string):
    """Does account_string represent a valid date?

    Basically, is root account one of
    equity/income/expense/asset/liability?"""
    try:
        sign_account(account_string)
        return True
    except KeyError:
        pass
    return False

def balance_amounts(transaction):
    "Return list of transaction's balances in each unit"
    result = []
    balances = defaultdict(int)
    for posting in transaction['postings']:
        sign = sign_account(posting['account'])
        units = posting['amount']['units']
        quantity = posting['amount']['quantity']
        balances[units] += quantity * sign
    for unit in balances.keys():
        result += [{'units': unit, 'quantity': balances[unit]}]
    return result

def is_balanced(transaction):
    "Is transaction balanced?"
    balances = balance_amounts(transaction)
    for balance in balances:
        if balance['quantity'] != 0:
            return False
    return True

def print_transactions(transactions):
    """Print list of transactions.

    Output should be in a form this code or John Wiegly's ledger can read."""
    for transaction in transactions:
        print transaction['date'], transaction['description']
        for posting in transaction['postings']:
            print ' ', posting['account'], ' ', format_amount(posting['amount'])
        print

def ensure_balanced(transactions):
    "Complain and exit if transaction isn't balanced."
    problem_found = False
    for transaction in transactions:
        if (not is_balanced(transaction)):
            problem_found = True
            sys.stderr.write("Line %d: Transaction does not balance. Date: '%s', description: %s.\n" %
                             (transaction['line'],transaction['date'],transaction['description']))
            for amount in balance_amounts(transaction):
                if amount['quantity'] != 0:
                    sys.stderr.write(" Imbalance amount: %s.\n" % format_amount(amount))
    if problem_found:
        sys.stderr.write("Exiting.\n")
        sys.exit(-1)

def ensure_date_sorted(transactions):
    "Make sure transactions are date sorted. Exit if not."
    if len(transactions) < 2:
        return
    last_date = transactions[0]['date']
    for transaction in transactions[1:]:
        ## XXX: Should throw an exception rather than exiting completely.
        if transaction['date'] < last_date:
            sys.stderr.write("Line %d: date: '%s' description: '%s' is not in date order.\n" %
                             (transaction['line'],transaction['date'],transaction['description']))
            sys.stderr.write("Exiting.\n")
            sys.exit(-1)
        last_date = transaction['date']

def is_prefix_of(list1, list2):
    "Is list1 a prefix of list2?"
    return list1 == list2[:len(list1)]

def contains_account(account_string1, account_string2):
    "Does account_string1 name a parent of, or same a/c as, account_string2?"
    regular1 = account_string_components(account_string1)['regular']
    regular2 = account_string_components(account_string2)['regular']
    return is_prefix_of(regular1, regular2)

def affects(transaction_or_posting, account_string):
    "Does transaction_or_posting affect named account?"
    if transaction_or_posting.has_key('postings'):
        return any([contains_account(account_string, p['account']) for p in transaction_or_posting['postings']])
    elif transaction_or_posting.has_key('account'):
        return contains_account(account_string, transaction_or_posting['account'])
    raise ValueError("Invalid transaction_or_posting in affects:", transaction_or_posting)

def filter_by_date(transactions, first_date = None, last_date = None):
    if first_date:
        first_date = dateutil.parser.parse(first_date)
        transactions = [t for t in transactions if dateutil.parser.parse(t['date']) >= first_date]
    if last_date:
        last_date = dateutil.parser.parse(last_date)
        transactions = [t for t in transactions if dateutil.parser.parse(t['date']) <= last_date]
    return transactions

def filter_by_account(transactions_or_postings, account_string):
    "Return transactions affecting named account?"
    return [t_or_p for t_or_p in transactions_or_postings if affects(t_or_p, account_string)]

# {{{ journal file parsing

def is_valid_date(date_string):
    "Does date_string represent a valid date?"
    try:
        dateutil.parser.parse(date_string)
        return True
    except ValueError:
        pass
    return False

def reformat_date(date_string):
    "Convert known valid date string, to iso-formatted date."
    return dateutil.parser.parse(date_string).isoformat()[:10]

def parse_first_line(line_number, line):
    """parse string containing first line of a transaction.

    Format of these lines is date-token description or description."""
    line = line.strip()
    split = line.split()
    date_string = split[0]
    description_string = line[len(date_string):].strip()

    if not is_valid_date(date_string):
        ## XXX: Should throw an exception rather than exiting completely.
        sys.stderr.write("Line %d: Invalid date: '%s' in transaction '%s'\n" %
                         (line_number, date_string, line))
        sys.stderr.write("Exiting.\n")
        sys.exit(-1)
    return {'line': line_number,
            'date': reformat_date(date_string),
            'description': description_string}


def verify_balance(verification, account_tree, verbose):
    account_string = verification['account']
    amount = verification['amount']
    actual_balances  = find_account(account_string, account_tree)['balances']

    if (extract_single_unit_amount(actual_balances) == amount):
        if (verbose):
            print "Verified:", verification['date'], verification['account'], format_amount(amount)
    else:
        verify_failed = True
        sys.stderr.write("FAILED: verify-balance for account '%s' at %s. Expected balance: %s. Actual balance: %s.\n" %
                         (account_string, verification['date'], format_amount(amount), format_single_unit_amount(actual_balances)))

def verify_balances(transactions, verifications, verbose, exit_on_failure):
    """Check that all assertions re account balances in verifications
    are true.
    Account balance assertions do not need to be written in date
    order. There is probably value in allowing these to be out of
    order in the file wrt the transactions. There is probably also
    value in allowing them to be in arbitrary order themselves. For
    example, we might have a bunch of assertions grouped by account
    rather than by date, at the start of the transactions file."""

    verify_failed = False

    verifications = sorted(verifications, key=lambda x: x['date'])
    account_tree = account_tree_from_transactions(transactions)
    for transaction in transactions:
        if len(verifications) > 0 and transaction['date'] > verifications[0]['date']:

            verify_balance(verifications[0], account_tree, verbose)
            verifications = verifications[1:]

        for posting in transaction['postings']:
            book_posting(posting, account_tree)

    while len(verifications) > 0:
        verify_balance(verifications[0], account_tree, verbose)
        verifications = verifications[1:]

    if exit_on_failure and verify_failed:
        sys.stderr.write("Verify balance operation failed.\nExiting.\n")
        sys.exit(-1)
    return account_tree

def parse_balance_verify(line_number, line, adjust_sign):
    """parse string containing a balance verification/assertion.

    Format is:

      VERIFY-BALANCE <date> <account> <amount>

    For example:
      "VERIFY-BALANCE 2012-12-31 Assets:Cash $10"."""

    line = line.strip()
    split = line.split()

    if len(split) <> 4:
        sys.stderr.write("Line %d: Invalid VERIFY-BALANCE operation:\n  %s\n" %
                         (line_number, line))
        sys.stderr.write("It should look like this:\n  VERIFY-BALANCE <date> <account> <amount>\nbut line %d contains %d elements (not 4).\n"%
                         (line_number, len(split)))
        sys.stderr.write("Exiting.\n")
        sys.exit(-1)

    date_string = split[1]
    account_string = split[2]
    amount_string = split[3].translate(None, "$")

    if not is_valid_account_string(account_string):
        sys.stderr.write("Line %d: invalid account string: '%s'.\n" %
                         (line_number, account_string))
        sys.stderr.write("Exiting.\n")
        sys.exit(-1)

    if not is_valid_date(date_string):
            sys.stderr.write("Invalid date: '%s'.\nExiting.\n" % date_string)
            sys.exit(-1)

    if adjust_sign:
        amount = parse_amount_adjusting_sign(account_string, amount_string)
    else:
        amount = parse_amount(amount_string)

    return {'date': date_string,
            'account': account_string,
            'amount': amount}

def parse_posting(line_number, line, adjust_sign):
    """parse string containing a posting.

    Format is account-name amount-with-unit/ccy.
    For example: "Expenses:Petrol $10"."""
    line = line.strip()
    split = line.split()
    account_string = split[0]
    amount_string = split[1].translate(None, "$")

    if not is_valid_account_string(account_string):
        sys.stderr.write("Line %d: invalid account string: '%s'.\n" %
                         (line_number, account_string))
        sys.stderr.write("Exiting.\n")
        sys.exit(-1)

    if adjust_sign:
        amount = parse_amount_adjusting_sign(account_string, amount_string)
    else:
        amount = parse_amount(amount_string)

    return {'line': line_number,
            'account': account_string,
            'amount': amount}

def is_balance_verify_line(line):
    "Does line contain a balance-verification assertion?"
    items = line.strip().split()
    return (len(items) > 0) and (items[0].upper() == "VERIFY-BALANCE")

def parse_transactions(lines, adjust_signs):
    "Convert list of lines from journal file to list of transactions."
    transactions = []
    verify_balances = []
    transaction = {}
    postings = []
    line_count = 0
    for line in lines:
        line = line.strip()
        if line.startswith("%") or line.startswith("#"):
            ## Lines beginning with '#' or '%' are treated as
            ## blanks/comments A comment can't begin at the end of a
            ## line that contains something else, though.
            line = ''
        line_count += 1
        if len(line) == 0:
            ## A blank line - possibly after a transaction
            if transaction:
                transaction['postings'] = postings
                transactions += [transaction]
                transaction = {}
                postings = []
        else:
            ## non-blank line
            if is_balance_verify_line(line):
                verify_balances += [parse_balance_verify(line_count, line, adjust_signs)]
            elif not transaction:
                transaction = parse_first_line(line_count, line)
            else:
                postings += [parse_posting(line_count, line, adjust_signs)]
    if transaction:
        transaction['postings'] = postings
        transactions += [transaction]
    return {'transactions' : transactions,
            'verify-balances' : verify_balances}

def parse_file(fname, adjust_signs):
    "convert text in fname into list of transactions."
    with open(fname) as infile:
        return parse_transactions(infile.readlines(), adjust_signs)

# }}}

def extract_accounts(transactions):
    ## XXX: I believe this is useless and not used
    """extract the accounts named in transactions to a dictionary.

    Account names are case-insensitive, but we remember the case
    the first time we see each account name."""
    accounts = {}
    for transaction in transactions:
        for posting in transaction['postings']:
            account = posting['account']
            as_upper = account.upper()
            if not accounts.has_key(as_upper):
                accounts[as_upper] = account
    return accounts

def print_accounts(accounts_dict):
    "Print chart of accounts represented in ACCOUNTS_DICT to stdout."
    for line in chart_of_accounts(accounts_dict):
        print line

def chart_of_accounts(accounts_dict, prefix= "", indent=""):
    """Return list of strings describing structure of accounts.

    accounts_dict represents hierachical structure of accounts."""
    result = []
    accounts =  accounts_dict.keys()
    accounts.sort()
    for account in accounts:
        account_name = accounts_dict[account]['name']
        sub_accounts = accounts_dict[account]['sub_accounts'].keys()
        has_own_postings = accounts_dict[account]['has_own_postings']

        if len(sub_accounts) == 0:
            result += [indent + prefix + account_name]
        elif (len(sub_accounts) == 1 and not has_own_postings):
            result += chart_of_accounts(accounts_dict[account]['sub_accounts'], prefix+account_name+":", indent)
        else:
            result += [indent + prefix + account_name]
            result += chart_of_accounts(accounts_dict[account]['sub_accounts'], "", indent+"  ")
    return result

def account_string_components(account_string):
    """Split account_string into components.

    Returns two versions:
    * 'original' with original case/spelling, and
    * regular with upper-cased spelling, and singular names converted
      to plural to increase consistency."""
    original = account_string.split(':')
    regular = [root_account_name(account_string)]
    for component in original[1:]:
        regular += [component.upper()]
    return {'original' : original,
            'regular': regular}

def _make_account(name):
    "Build a dictionary that functions as an account_tree structure."
    return {'name': name,
            'sub_accounts' : {},
            'balances' : {},
            'has_own_postings' : False}

def _ensure_sub_account(account,
                        sub_account_regular_name,
                        sub_account_original_name):
    "Internal. Make sure account is direct descendant of account, and return it."
    if not account['sub_accounts'].has_key(sub_account_regular_name):
        account['sub_accounts'][sub_account_regular_name] = _make_account(sub_account_original_name)
    return account['sub_accounts'][sub_account_regular_name]

def _ensure_sub_accounts(account_string, root_account):
    """Internal. Ensure all of account_string's components are present under root.

    We also mark the leaf node as having its own postings."""

    components = account_string_components(account_string)
    original = components['original']
    regular = components['regular']
    account = root_account
    while len(original) > 0:
        account = _ensure_sub_account(account, regular[0], original[0])
        if len(original) == 1:
            account['has_own_postings'] = True
        original = original[1:]
        regular = regular[1:]

def account_tree_from_transactions(transactions):
    "Build account tree structure from transactions."
    root = _make_account('')
    for transaction in transactions:
        for posting in transaction['postings']:
            _ensure_sub_accounts(posting['account'], root)
    return root['sub_accounts']

def account_tree_from_account_strings(account_strings):
    "Build account tree structure from list of account_strings."
    root = _make_account('')
    for account_string in account_strings:
        _ensure_sub_accounts(account_string, root)
    return root['sub_accounts']

def find_original_prefix(account_string, account_tree):
    "Return the original prefix of the account in tree specified by account_string."
    try:
        components = account_string_components(account_string)['regular']
        account_name = components[0]
        account_tree = account_tree[account_name]
        result = ""
        while len(components) > 1:
            components = components[1:]
            account_name = components[0]
            result += account_tree['name']
            account_tree = account_tree['sub_accounts'][account_name]
        if len(result) > 0:
            result += ":"
        return result
    except KeyError:
        raise ValueError("Account not found: '%s'"%account_string)

def find_account(account_string, account_tree):
    "Return the part of account_tree named by account_string."

    try:
        components = account_string_components(account_string)['regular']
        account_name = components[0]
        account_tree = account_tree[account_name]
        while len(components) > 1:
            components = components[1:]
            account_name = components[0]
            account_tree = account_tree['sub_accounts'][account_name]
        return account_tree
    except KeyError:
        raise ValueError("Account not found: '%s'"%account_string)

def account_and_parents(account_string, account_tree):
    "Return nodes of account_tree that related to account_string or it's parents."
    components = account_string_components(account_string)['regular']
    this_account_string = components[0]
    account_strings = [this_account_string]
    for component in components[1:]:
        this_account_string += ":" + component
        account_strings += [this_account_string]
    result = []
    for account_string in account_strings:
        result += [find_account(account_string, account_tree)]
    return result

def account_string_and_parents(account_string):
    "Return regularised name for account and all of it's parent accounts."
    components = account_string_components(account_string)['regular']
    this_result = components[0]
    result = [this_result]
    for component in components[1:]:
        this_result += ":" + component
        result += [this_result]
    return result

def book_posting(posting, account_tree):
    "Update balances in account_tree using account & amount from posting."

    amount = posting['amount']
    units = amount['units']
    quantity = amount['quantity']
    account_string = posting['account']

    find_account(account_string, account_tree)['has_own_postings'] = True

    for account in account_and_parents(account_string, account_tree):
        balances = account['balances']
        if balances.has_key(units):
            balances[units]['quantity'] += quantity
        else:
            balances[units] = dict(amount)

def calculate_balances(transactions, as_at_date):
    "Return account tree with balances from transactions."
    account_tree = account_tree_from_transactions(transactions)
    for transaction in transactions:
        if ((not as_at_date) or (transaction['date'] <= as_at_date)):
            for posting in transaction['postings']:
                book_posting(posting, account_tree)
    return account_tree

def single_unit_balances_helper(accounts_dict, account_names, prefix= "", indent=0, print_stars_for_org_mode=False):
    """Internal.

    Return list of (amount, account-name) string pairs showing a/c structure."""

    result = []

    if len(account_names) > 0:
        for account_name in account_names:
            account = find_account(account_name, accounts_dict)
            result += single_unit_balances_helper({account['name']: account}, [],
                                                  prefix=find_original_prefix(account_name, accounts_dict),
                                                  indent=indent,
                                                  print_stars_for_org_mode=print_stars_for_org_mode)
        return result
    ## else account_names = [] => print for all accounts
    accounts =  accounts_dict.keys()
    accounts.sort()

    for account in accounts:
        account_name = accounts_dict[account]['name']
        sub_accounts = accounts_dict[account]['sub_accounts'].keys()
        balances  = accounts_dict[account]['balances']
        has_own_postings = accounts_dict[account]['has_own_postings']
        amount_string = format_nil_or_single_unit_amount(balances)
        if print_stars_for_org_mode:
            stars = ("*"*(indent+1))
        else:
            stars=""
        if len(sub_accounts) == 0:
            result += [(stars, amount_string, (" " * (indent*2)) + prefix + account_name)]
        elif (len(sub_accounts) == 1 and not has_own_postings):
            result += single_unit_balances_helper(accounts_dict[account]['sub_accounts'], [], prefix+account_name+":", indent, print_stars_for_org_mode)
        else:
            result += [(stars, amount_string, (" " * (indent*2)) + prefix + account_name)]
            result += single_unit_balances_helper(accounts_dict[account]['sub_accounts'], [], "", indent+1, print_stars_for_org_mode)
    return result


def validate_one_date_or_two(as_at_date, first_date, last_date):
    if (as_at_date):
        # If you specify as-at-date, you can't specify first or last dates
        if first_date:
            sys.stderr.write("Error: first-date: %s specified in addition to as-at-date '%s'.\n"
                             "Exiting."%(first_date, as_at_date))
            sys.exit(-1)
        if last_date:
            sys.stderr.write("Error: last-date: %s specified in addition to as-at-date '%s'.\n"
                             "Exiting."%(last_date, as_at_date))
            sys.exit(-1)

    if (first_date):
        # If you specify first date, also need last-date, and no as-at-date.
        if not last_date:
            sys.stderr.write("Error: first-date: %s specified, but last-date unspecified.\n"
                             "Exiting."%(first_date))
            sys.exit(-1)
    if last_date:
        if not first_date:
            sys.stderr.write("Error: last-date: %s specified, but first-date unspecified.\n"
                             "Exiting."%(last_date))
            sys.exit(-1)

def print_single_unit_balances(transactions, account_names, print_stars_for_org_mode, as_at_date, first_date, last_date):
    """Print balances of accounts. Assumes only 1 unit/ccy per account.

    If account_names = [], assume all accounts, otherwise just the specified accounts.
    """

    validate_one_date_or_two(as_at_date, first_date, last_date)

    if (not first_date) and (not last_date):

        transactions = filter_by_date(transactions, last_date = as_at_date)
        balance_text = single_unit_balances_helper(calculate_balances(transactions, as_at_date),
                                                   account_names,
                                                   print_stars_for_org_mode=print_stars_for_org_mode)
        for line in join_columns(justify_columns(balance_text, "LRL")):
            print line
    if first_date and last_date:
        transactions = filter_by_date(transactions, last_date = last_date)
        first_text = single_unit_balances_helper(calculate_balances(transactions, first_date),
                                                 account_names,
                                                 print_stars_for_org_mode=print_stars_for_org_mode)
        last_text = single_unit_balances_helper(calculate_balances(transactions, last_date),
                                                account_names,
                                                print_stars_for_org_mode=False)

        new_text = [(first_text[0][0], first_date, last_date, "Change","Account")]
        for i in range(len(first_text)):
            new_text += [tuple(list(first_text[i][:2]) + [last_text[i][1]]
                               + [format_amount(difference_nil_or_single_unit_amount(parse_amount(last_text[i][1]),
                                                                                     parse_amount(first_text[i][1])))]
                               + [last_text[i][2]])]

        for line in join_columns(justify_columns(new_text , "LRRRL")):
            print line
            format_amount(difference_nil_or_single_unit_amount(parse_amount("-$1,900.00"), parse_amount("$1,900.00")))

def calculate_register(transactions, account_string, first_date, last_date):
    "Calculate text showing effect of transactions on relevant account."
    result = []
    transactions = filter_by_account(transactions, account_string)
    account_tree = account_tree_from_transactions(transactions)
    for transaction in transactions:
        for posting in filter_by_account(transaction['postings'], account_string):
            book_posting(posting, account_tree)
            if (((not first_date) or (transaction['date'] >= first_date)) and
                ((not last_date) or (transaction['date'] <= last_date))):
                result += [(transaction['date'],
                            format_single_unit_amount(find_account(account_string, account_tree)['balances']),
                            format_amount(posting['amount']),
                            posting['account'],
                            transaction['description'])]
    return result

def print_register(transactions, account_string, reverse_print_order, first_date, last_date):
    data = calculate_register(transactions, account_string, first_date, last_date)
    data = rjust_column(data, 0)
    data = rjust_column(data, 1)
    data = rjust_column(data, 2)
    data = ljust_column(data, 3)
    data = join_columns(data, '\t')

    if reverse_print_order:
        data.reverse()
    for line in data:
        print line

def main():
    "Program that runs if invoked as a script."
    parser = argparse.ArgumentParser(description='Command-line, double-entry accounting in python.')
    parser.add_argument('file', metavar='FILE',
                        help='the input journal file to read from')
    parser.add_argument('--tweak-signs-of-input-amounts',
                        default=False,
                        action="store_true",
                        help="negate amounts from input file for equity/liabilities/income")
    parser.add_argument('--verbose',
                        default=False,
                        action="store_true",
                        help="print extra information while running")
    parser.add_argument('--show-balance-verifications',
                        default=False,
                        action="store_true",
                        help="print details of account verifications")
    parser.add_argument('--ignore-balance-verification-failure',
                        default=False,
                        action="store_true",
                        help="do not exit if an verify-balance test fails")
    parser.add_argument('--ignore-transactions-outside-dates',
                        default=False,
                        action="store_true",
                        help="Ignore any transactions outside the relevant dates.")
    parser.add_argument('--print-transactions',
                        default=False,
                        action="store_true",
                        help="print a re-formatted version of FILE")
    parser.add_argument('--print-chart-of-accounts',
                        default=False,
                        action="store_true",
                        help="print structure of account hierarchy found in FILE")
    parser.add_argument('--print-balances', nargs='*', metavar='ACCOUNT',
                        help="print balances or specified accounts. (All accounts if none specified.)")
    # parser.add_argument('--balance', nargs='*', metavar='ACCOUNT',
    #                     help='show account balances (all accounts if none specified)')
    parser.add_argument('--print-stars-for-org-mode',
                        default=False,
                        action="store_true",
                        help="print stars for indentation so file can be collapsed using emacs' org-mode")
    parser.add_argument('--reverse-print-order',
                        default=False,
                        action="store_true",
                        help="Reverse order lines are printed (--print-xyz)")

    # parser.add_argument('--balance', nargs='*', metavar='ACCOUNT',
    #                     help='show account balances (all accounts if none specified)')

    parser.add_argument('--print-register', metavar='ACCOUNT',
                        help='print the running balance for a specified account')

    parser.add_argument('--as-at', metavar='DATE',
                        help="print report as-at")

    parser.add_argument('--first-date', metavar='FIRST-DATE',
                        help="ignore or don't report transactions before FIRST-DATE")

    parser.add_argument('--last-date', metavar='LAST-DATE',
                        help="ignore or don't report transactions after LAST-DATE")

    args = parser.parse_args()

    parsed_file = parse_file(args.file, args.tweak_signs_of_input_amounts)
    transactions = parsed_file['transactions']
    verifications = parsed_file['verify-balances']

    if (args.as_at):
        if not is_valid_date(args.as_at):
            sys.stderr.write("Invalid as-at-date: '%s'.\nExiting.\n" % args.as_at)
            sys.exit(-1)
        else:
            print "# As at:", args.as_at

    if (args.first_date):
        if not is_valid_date(args.first_date):
            sys.stderr.write("Invalid first-date: '%s'.\nExiting.\n" % args.first_date)
            sys.exit(-1)
        else:
            print "# First date:", args.first_date

    if (args.last_date):
        if not is_valid_date(args.last_date):
            sys.stderr.write("Invalid last-date: '%s'.\nExiting.\n" % args.last_date)
            sys.exit(-1)
        if args.first_date and (args.first_date > args.last_date):
            sys.stderr.write("First date '%s' is after last-date: '%s'.\nExiting.\n"
                             % (args.first_date, args.last_date))
            sys.exit(-1)
        if args.first_date and (args.first_date == args.last_date):
            sys.stderr.write("First date '%s' same as last-date: '%s'.\nExiting.\n"
                             % (args.first_date, args.last_date))
            sys.exit(-1)
        else:
            print "# Last date:", args.last_date

    verify_balances(transactions, verifications,
                    (args.verbose or args.show_balance_verifications),
                    not args.ignore_balance_verification_failure)
    ensure_date_sorted(transactions)
    ensure_balanced(transactions)

    if (args.ignore_transactions_outside_dates):
        print "# Ignoring transactions earlier/later than specified dates."
        transactions = filter_by_date(transactions, args.first_date, args.last_date)

    if (args.print_chart_of_accounts):
        for line in chart_of_accounts(account_tree_from_transactions(transactions)):
            print line

    if (args.print_transactions):
        relevant_transactions = filter_by_date(transactions, args.first_date, args.last_date)
        print_transactions(relevant_transactions)


    if (args.print_balances <> None):
        print_single_unit_balances(transactions, args.print_balances, args.print_stars_for_org_mode, args.as_at, args.first_date, args.last_date)

    if (args.print_register):
        print_register(transactions, args.print_register, args.reverse_print_order, args.first_date, args.last_date)

if __name__ == "__main__":
    main()
