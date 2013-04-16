# Ledger.py: command-line, double-entry accounting in python

**Ledger.py** is a simple, command-line, double-entry accounting
system. It reads transactions written in a simple format from a
text file and produces summary reports in text.

Because transaction data is stored as text, it can be managed
using a version control system like git. This makes it easy
to maintain an audit trail.

Ledger.py is like John Wiegley's
[Ledger](http://www.ledger-cli.org/), but simpler.

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

You can find _some_ documentation on how to use the program in the
```Introduction.md``` file in the doc folder. There's not much
documentation yet, but ledger.py is simple.

### Requirements

As far as I know, ledger.py needs only Python 2.7. I am currently using it with Python 2.7.2+.

#### Testing

If you have nosetests installed, you can also run some tests. They are
not comprehensive. If you have coverage installed, you can also look
at the test coverage like this: ```nosetests --with-coverage
--cover-package=ledger```.

## Status

I am using this program on a daily basis to do real work. I believe that what _has_ been implemented is more
or less correct. However, this program hasn't been extensively tested,
so you use it at your own risk.

Lots of useful easy-to-implement features have not yet been
implemented. I am currently (April 2013) attempting to implement one
or two of the missing features per week.

## Origins

Ledger.py is similar to, and partly inspired by, John Wiegley's Ledger: http://www.ledger-cli.org/.

Ledger.py is also similar to some older double-entry accounting
software I wrote using wxPython in 2004. Although that program had a GUI, and
I used it for nearly ten years, it was more complex than ledger.py,
and I found it less convenient to use.
