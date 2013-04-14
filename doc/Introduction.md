# Ledger.py: command-line, double-entry accounting in python

Ledger.py is a simple, command-line, double-entry accounting system.
It reads transactions written in a simple format from a text file and
produces summary reports in text.

Because transaction data is stored as text, it can be managed using a version control system like git.
This makes it easy to maintain an audit trail.

This introduction should give enough basic information to show you how to use the program.
A Reference document should eventually provide more detailed information, but it hasn't been written yet.

## Getting started

The program is currently contained in a single python file. You can grab it and try it out like this:
```
# Grab the code
git clone git://github.com/mafm/ledger.py
cd ledger.py

# Look at some examples
./ledger.py examples/sample.transactions --print-balances
./ledger.py examples/sample.transactions --print-register Expenses
./ledger.py examples/sample.transactions --print-register Expenses:Electricity
```

## The Input File

**Ledger.py** reads transaction data from a simple text input file.

Here is a simple example input file with three transactions:
```
2013-01-01 I began the year with $1000 in my cheque account.
  Assets:Bankwest:Cheque      $1,000
  Equity:OpeningBalances      $1,000

2013-01-05 I bought some groceries and paid using the cheque account.
  Expenses:Food:Groceries    $98.53
  Assets:Bankwest:Cheque    -$98.53
  
2013-01-10 I bought some petrol, and paid using a credit card
  Expenses:Motor:Fuel    $58.01
  Liabilities:Bankwest:Visa   $58.01
```

### Transactions

A transaction contains:
- a date,
- a description, or narration, and
- a set of postings.

Postings contains:
- an account name, and
- an amount that the posting will change the account by.

#### The accounting equation

Transactions need to *balance*. If the input file contains a transaction that doesn't balance, **ledger.py** will exit
after printing an error message.

**Ledger.py** understands 5 basic types of accounts:
- assets,
- liabilities,
- income,
- expenses, and
- equity.

The basic rule of accounting is that:
```
Assets + Expenses = Income + Liabilities + Equity.
```
If a transaction increases an asset or expense account, it also needs to post a corresponding increase to income,
liability, or equity, in order to balance.

#### Transaction Syntax
Transactions in the input file look like this:
```
<date> <description>
 <account> <amount>
 <account> <amount>
 ...
 <blank line>
```
Transactions are terminated by blank lines. You don't need to indent the lines that represent transaction postings,
but the input file is easier to read if you do.

#### Transactions need to be in date order

**Ledger.py** forces you to write transactions in date order.
If transactions are not in date order, the program will exit with an error message after reading the file.
I find this useful, because it makes the input file easier to read, and helps ensure that I get the right
date on transactions.

### Comments

Lines in the input file beginning with '%' or '#' are treated as blank lines. The '%' and '#'
are not treated as comments unless they are at the first non-blank characters in a line, so you can't
put a comment at the end of a line containing something else.

## Operations

You can currently do the following things with **ledger.py**:
- --print-balances - show the current balances of accounts mentioned in the input file
- --print-register - show a running balance for a specified account
- --print-chart-of-accounts - show the current structure of the accounts
- --print-transactions - print a re-formatted copy of the transactions in the input file

### Print Balances

This currently just shows the final balance of the accounts mentioned in the input file. There is some slightly
clever formatting that any hierarchical structure in the accounts.

Example:
```
./ledger.py examples/sample.transactions --print-balances
```

### Print Register

This shows the transactions affecting an account, and the running balance of that account as the transactions
are encountered.

Examples:
```
./ledger.py examples/sample.transactions --print-register Expenses:Electricity
./ledger.py examples/sample.transactions --print-register Expenses
```
Note that if you specify an account with sub-accounts, transactions affecting sub-accounts will be printed, but
the running balance for the specified account will be shown, instead of the running balance for the transaction's
sub-account:
```
$ ./ledger.py examples/sample.transactions --print-register Expenses
2013-01-05       $98.53  $98.53 Expenses:Food:Groceries I bought some groceries and paid using the cheque account.
2013-01-10      $156.54  $58.01 Expenses:Motor:Fuel     I bought some petrol, and paid using a credit card.
2013-01-15      $436.96 $280.42 Expenses:Electricity    I paid my electricity bill.
```


### Print Chart of Accounts
This currently just shows the hierarchical structure of the accounts mentioned in the input file.

```
./ledger.py examples/sample.transactions --print-chart-of-accounts
```

### Print Transactions

This might be useful if you want to get a cleaned-up version of an input file that's consistently formatted.

Example:
```
./ledger.py examples/sample.transactions --print-transactions
```

## References

There is a fairly extensive online textbook on accounting here:
http://www.principlesofaccounting.com

There is an explanation of how multi-currency accounting should be done here:
http://www.mscs.dal.ca/~selinger/accounting
