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

# Generate some example reports
./ledger.py examples/sample.transactions --print-balances
./ledger.py examples/sample.transactions --print-register Expenses
./ledger.py examples/sample.transactions --print-register Expenses:Electricity

# Generate a highly structured report across multiple dates in an Excel-readable report
./ledger.py examples/sample.transactions --generate-excel-report foo --dates 2012-12-31 2013-12-31
```

I like the Excel-readable report output. It's a lot more useful than
plain text output. If you try this out, note that you use the +/-
buttons in the left margin control the level of indentation displayed
in the "Balances" worksheet. Unfortunately, the Excel-readable output
file is generated with all indentation levels opened, and the columns
at default widths. Otherwise, I think it's pretty good. It shows:
- balances at dates,
- balance differences between dates, and
- how/when transactions affected the balances/differences.

## Outline

The rest of this document is structured roughly like this:
- [Input File](#the-input-file)
  - [Transactions](#transactions)
  - [Other things that can appear in the input file](#other-things-that-can-appear-in-the-input-file)
     - [Instructions](#instructions)
- [Reports](#reports)
  - [Excel-readable Reports](#excel-readable-reports)
  - [Reports in plain text](#reports-in-plain-text)
    - [Print Balances](#print-balances)
    - [Print Register](#print-register)
    - [Print Chart Of Accounts](#print-chart-of-accounts)
    - [Print Transactions](#print-transactions)

## The Input File

Ledger.py reads transaction data from a simple text input file.

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

A transaction consists of:
- a date,
- a description (or 'narration') and
- a set of postings.

A posting consists of:
- an account name, and
- an amount by which the posting changes the account's balance.

#### Transaction Syntax
Transactions in the input file look like this:
```
<date> <description>
 <account> <amount>
 ...
 <account> <amount>
```
Transactions are separated by blank lines. You don't need to indent
the lines that represent transaction postings, but the input file is
easier to read if you do.

Account names should not contain whitespace characters, and can be a
colon separated sequence of names that reflect a hierarchical
structure amount accounts. The first component of an account name
should be designate one of the [five basic account
types](#the-accounting-equation).

#### The accounting equation

Transactions need to *balance*. If the input file contains a
transaction that doesn't balance, ledger.py will exit after
printing an error message.

Ledger.py understands 5 basic types of accounts:
- assets,
- liabilities,
- income,
- expenses, and
- equity.

The basic rule of accounting is that:
```
Assets + Expenses = Income + Liabilities + Equity.
```
If a transaction increases an asset or expense account, it also needs
to post a corresponding increase to an income,
liability, or equity account, in order to balance.

#### Transactions need to be in date order

Ledger.py forces you to write transactions in date order. If
transactions are not in date order, the program will exit with an
error message after reading the file.  This is useful, because it
makes the input file easier to read, and helps ensure that
transactions have correct dates.

Dates should be written in [ISO format](http://xkcd.com/1179) like
this: ```2013-02-28```. Ledger.py _will_ accept dates in other
formats, but it converts them to ISO format internally, and if
you use the ```--print-transactions``` command, they will be printed
that way.

### Other things that can appear in the input file

In addition to transactions, ledger.py's input file can contain some
other optional information:
- comments, and
- instructions.

### Comments

Lines in the input file beginning with '%' or '#' are treated as blank lines. The '%' and '#'
characters have no effect unless they are the first non-blank characters in a
line, so you can't put a comment at the end of a line containing something else.

### Instructions

'Instructions' let you tell ledger.py things like what the default
currency should be, or that it should check that a particular account
has the correct balance for a particular date. At the moment, the
only instructions ledger.py knows about are 'verify-balance'
instructions. More will be added later to allow you to do other things
like specify the default currency for an input file, or tell ledger.py
what the market value of an asset was at a particular date.

#### Verify-Balance instructions

To make sure that the balance in an account is
correct at a particular date, you can add lines like this:
```
VERIFY-BALANCE 2013-02-01 Assets:Bankwest:Cheque $621.05
```
to an input file. When ledger.py reads the input file, it will
complain and exit if the balance in the account is not as specified at
at the end of the day on the specified date. You can use the option
```--ignore-balance-verification-failure``` to prevent ledger.py
quitting due to incorrect balances. This might be useful if you want to use
ledger.py to examine the transactions and find the problem.

If you want to see an
explicit confirmation that each of the verify-balance checks has been
successful, use the ``--verbose`` or
``--show-balance-verifications``` options.

##### Where verify-balance instructions can be specified

Unlike transactions, the verify-balance instructions in an input file
do _not_ need to be written in date order. You can put them in any
order you like, and you can also put them between transactions. If you want to, you can put all verify-balance instructions near the
beginning of an input file, grouped by account name, and then by date.

Legder.py extracts all verify-balance instructions from a file and
checks them against transactions once the file has been read
completely.

## Reports

### Excel-readable Reports

Ledger.py can generate an nicely formatted Excel-readable report using
these options:


```--generate-excel-report <output-filename> --dates <YYYY-MM-DD> <YYYY-MM-DD> ...```

This generated report will include:
- A "Balance Report" worksheet showing:
  - the balance of each account at each specified date,
  - differences between the specified dates, including a total difference between the last and first dates, and
  - a list of the transactions affecting each account
- An "Account Structure" worksheet showing the tree accounts named in the input file.
- A "Transactions" worksheet list of all transactions, with details.

### Reports in plain text

Ledger.py can generate text reports from an input file using these main options:
- --print-balances - show balances of accounts mentioned in the input file
- --print-register - show a running balance for a specified account
- --print-chart-of-accounts - show the current structure of the accounts
- --print-transactions - print a re-formatted copy of the transactions in the input file

#### Print Balances

This shows the balances of the accounts listed in the input file with
intelligent indentation that shows hierarchical structure within the
account.

This report can show either:
- balances with _all_ available transactions included,
- balances including transactions up to a certain date, or
- balances on two different dates and the changes between those.
You can also give a list of account names to include in the report. If
you do this, all other accounts will be ignored.

Relevant optional arguments:
- ```<account-name> ... <account-name>``` - list of accounts to print balances for
- ```--as-at <date>``` - print balances as at this date
- ```--first-date <last-date>``` and  ```--last-date <last-date>```- print balances at these two dates, and the difference between them

Examples:
```
./ledger.py examples/sample.transactions --print-balances
./ledger.py examples/sample.transactions --print-balances --as-at 2013-01-05
./ledger.py examples/sample.transactions --print-balances --as-at 2013-01-15
./ledger.py examples/sample.transactions --print-balances --first-date 2013-01-05 --last-date 2013-01-15
./ledger.py examples/sample.transactions --print-balances assets expenses --as-at 2013-01-15
./ledger.py examples/sample.transactions --print-balances assets expenses:motor --as-at 2013-01-15
./ledger.py examples/sample.transactions --print-balances  --print-balances expenses assets --first-date 2013-01-05 --last-date 2013-03-02
```

#### Print Register

This shows the transactions affecting an account, and the running balance of that account as the transactions
are encountered.

Mandatory argument:
- ```<account>``` the account whose register is to be printed.

Relevant optional arguments:
- ```--first-date <first-date>``` - don't print details for transactions before this date.
- ```--last-date <last-date>``` - don't print details for transactions after this date
- ```--include-related-postings``` - print all postings in transactions affecting <account>. Without this option, only parts of the transaction that affect ```<account>``` will be shown.
- ```--ignore-transactions-outside-dates``` - start the running balance from zero as at ```<first-date>```, so balances
shown for the relevant account will not reflect earlier transactions. By default, transactions before
```<first-date>``` _will_ affect the balance, but ledger.py will not print a line for those transactions
in the ```--print-register``` report.

Examples:
```
./ledger.py examples/sample.transactions --print-register Expenses:Electricity
./ledger.py examples/sample.transactions --print-register Expenses
./ledger.py examples/sample.transactions --print-register Expenses --first-date 2013-01-10
./ledger.py examples/sample.transactions --print-register Expenses --first-date 2013-01-10 --ignore-transactions-outside-dates
./ledger.py examples/sample.transactions --print-register Expenses --first-date 2013-01-10 --last-date 2013-01-12
./ledger.py examples/sample.transactions --print-register expenses --include-related-postings
```
Note that if you specify an account that has sub-accounts, transactions affecting the sub-accounts will be shown,
but the running balances shown will be the balance for the specified account, not the balance for the
transaction's sub-account:
```
$ ./ledger.py examples/sample.transactions --print-register Expenses
2013-01-05       $98.53  $98.53 Expenses:Food:Groceries I bought some groceries and paid using the cheque account.
2013-01-10      $156.54  $58.01 Expenses:Motor:Fuel     I bought some petrol, and paid using a credit card.
2013-01-15      $436.96 $280.42 Expenses:Electricity    I paid my electricity bill.
```


#### Print Chart of Accounts

This currently just shows the hierarchical structure of the accounts mentioned in the input file.

```
./ledger.py examples/sample.transactions --print-chart-of-accounts
```

### Print Transactions

This might be useful if you want to get a cleaned-up version of an input file that's consistently formatted. You
can also use this to print the subset of transactions that occur between two dates.

Relevant optional arguments:
- ```--first-date <first-date>``` - don't print transactions before this date
- ```--last-date <last-date>``` - don't print transactions after this date

Example:
```
./ledger.py examples/sample.transactions --print-transactions
./ledger.py examples/sample.transactions --print-transactions --first-date 2013-01-01
./ledger.py examples/sample.transactions --print-transactions --last-date 2013-01-12
./ledger.py examples/sample.transactions --print-transactions --first-date 2013-01-01 --last-date 2013-01-12
```

## More Information

There is a fairly extensive online textbook on accounting here:
http://www.principlesofaccounting.com

There is an explanation of how multi-currency accounting should be done here:
http://www.mscs.dal.ca/~selinger/accounting

The Australian Tax Office used to give away accounting software they thought was suitable for small businesses.
You can still download a copy of it here:
http://www.kilbot.com.au/2011/10/18/download-e-record/
