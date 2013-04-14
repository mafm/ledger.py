# Ledger.py: command-line, double-entry accounting in python

**Ledger.py** is a simple, command-line, double-entry accounting
system. It reads transactions written in a simple format from a
text file and produces summary reports in text.

Because transaction data is stored as text, it can be managed
using a version control system like git. This makes it easy
to maintain an audit trail.

## Requirements

If you want to use this program, you need only Python 2.7.2+ (as far
as I know). The program is currently contained in a single python
file.

### Testing

If you have nosetests installed, you can also run some tests. They are
not comprehensive.

## Status

I am using this software on a daily basis to do real work. To the best
of my knowledge, what _has_ been implemented works correctly.

Lots of useful easy-to-implement features have not yet been
implemented. I am currently (April 2013) attempting to implement one
or two of the missing features per week.

## Inspiration

**Ledger.py** is similar to, and partly inspired by, John Wiegley's Ledger: http://www.ledger-cli.org/.

**Ledger.py** is also similar to some older double-entry accounting
software I wrote using wxPython. Although that software had a GUI, and
I used it for several years, it was more complex than **ledger.py**,
and I found it less convenient to use.
