# Ledger.py: command-line, double-entry accounting in python

**Ledger.py** is a simple, command-line, double-entry accounting
system. It reads transactions written in a simple format from a
text file and produces summary reports in text.

Because transaction data is stored as text, it can be managed
using a version control system like git. This makes it easy
to maintain an audit trail.

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

There's not much documentation yet, but **ledger.py** is simple. You should be able to work out most
of what's going on by looking at the example input files and reading the code.

### Requirements

As far as I know, **ledger.py** needs only Python 2.7. I am currently using it with Python 2.7.2+.

#### Testing

If you have nosetests installed, you can also run some tests. They are
not comprehensive.

## Status

I am using this program on a daily basis to do real work. I believe that what _has_ been implemented is more
or less correct. However, this program hasn't been extensively tested. Use it at your own risk.

Lots of useful easy-to-implement features have not yet been
implemented. I am currently (April 2013) attempting to implement one
or two of the missing features per week.

## Origins

**Ledger.py** is similar to, and partly inspired by, John Wiegley's Ledger: http://www.ledger-cli.org/.

**Ledger.py** is also similar to some older double-entry accounting
software I wrote using wxPython in 2004. Although that program had a GUI, and
I used it for nearly ten years, it was more complex than **ledger.py**,
and I found it less convenient to use.
