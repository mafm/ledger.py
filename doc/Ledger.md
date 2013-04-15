# Why bother implementing something so similar to [Ledger](http://www.ledger-cli.org/)?

**Ledger.py** is like John Wiegley's
[Ledger](http://www.ledger-cli.org/), but simpler.

I used [ledger](http://www.ledger-cli.org/) for a while, and liked
using an accounting system that accepted input files written in plain
text, but there are several problems with
[ledger](http://www.ledger-cli.org/) that make **ledger.py**
worthwhile.

## Fragile Syntax

In general, the syntax of the input file
[ledger](http://www.ledger-cli.org/) reads seems fragile. I found I needed to
check its output reports fairly carefully after adding transactions to
the input file to avoid introducing errors.

In particular, [ledger](http://www.ledger-cli.org/) fails silently instead of complaining in the following situations:
- If the first line in a transaction begins with a space, [ledger](http://www.ledger-cli.org/) will ignore
  the whole transaction(!)
- If the amount in a posting is preceded by only a single space (not by several spaces or a tab character),
  the amount is interpreted as part of the account name, and a default amount is generated. This was never
  what I wanted.

I also didn't like the way Ledger automatically fills in the amount
for one posting if all the other postings of a transaction have
explicit amounts. Sometimes I attempted to manually write an amount
for a posting, but got the syntax wrong by leaving only a single space
between the account and the posted amount, and ledger automatically
calculated an amount that was different to the one I had manually
attempted to specify.

None of these problems are unmanageable, but I spent more time
checking and re-checking input data than I expected to.

## Debits and Credits, etc.

I _really_ do not like the way [ledger](http://www.ledger-cli.org/) deals
with ensuring transactions balance. Although
[ledger](http://www.ledger-cli.org/)'s way of doing this is simple and
neat, it makes things writing transactions unnecessarily confusing,
especially for people who already know something about accounting.

The basic rule of accounting is that transactions should obey the
'accounting equation':
```
Assets + Expenses = Income + Liabilities + Equity.
```
If a transaction increases an asset account, it should make a
corresponding increase to either an income, liabilities, or equity
account (or possibly _decrease_ an expenses account.) As long as the
changes on both sides are equal, the transaction _balances_. This is
the basis of double-entry accounting: money never comes into an account from
nowhere - it always moves from one account to another.

[Ledger](http://www.ledger-cli.org/) doesn't distinguish between the
accounts on the left and right hand sides of the accounting equation,
and expects the user to write negative amounts for changes to
accounts on the right-hand side (income, liabilities, and equity)
where the accounting equation would suggest you write a positive
amount. For example, the transaction below tells
[ledger](http://www.ledger-cli.org/) to *decrease* the amount in the
```Liabilities:MasterCard``` account by $10, to offset a $10 increase
in the expense account.
```
2006/10/15 Exxon
      Expenses:Auto:Gas        $10.00
      Liabilities:MasterCard  -$10.00
```

I found this confusing. It's not too bad when you're concentrating, or
looking at a simple example, but it's easy to slip up and tweak the sign
for the wrong account. For example, in the 'paying for fuel with a
credit-card' example, using a negative amount for the expense account
might also make sense at first glance, and if you're confused, you might
think of writing the transaction like this, which
[ledger](http://www.ledger-cli.org/) would also accept (although it wouldn't
have the desired effect):
```
2006/10/15 Exxon
      Expenses:Auto:Gas      -$10.00
      Liabilities:MasterCard  $10.00
```

[Describing transactions in terms of debits and credits]
(http://en.wikipedia.org/wiki/Debits_and_credits) _is_ pointlessly
complicated, but writing transactions using the normal accounting
conventions (where an increase in a liability will balance an equal
increase in an expense account) simplifies things.

**Ledger.py** understands that accounts on the left-hand side of the
accounting equation are different to (and balance against) the
accounts on the right-hand side. This means that you can represent
the Exxon transaction in the normal way, like this:
```
2006/10/15 Exxon
 Expenses:Auto:Gas $10.00
 Liabilities:MasterCard $10.00
```

## Extra Operations/Reports

I also wanted to generate some reports that
[ledger](http://www.ledger-cli.org/) didn't support out of the box,
and it seemed simpler to implement the relevant code in python than
to build something on top of [ledger](http://www.ledger-cli.org/) to
do what I wanted.

I should give some examples here, but probably haven't implemented the
relevant reports yet.
