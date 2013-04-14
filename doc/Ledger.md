# What's wrong with [Ledger](http://www.ledger-cli.org/)?

I used John Wiegley's [ledger](http://www.ledger-cli.org/) for a while, but there are several things I dislike
about it that made writing something simpler in python worthwhile.

## Fragile Syntax

In general, the syntax of the input file [ledger](http://www.ledger-cli.org/) reads seems fragile. You need to check its output reports fairly carefully after adding transactions to the input file 
if you want to avoid errors.

In particular, [ledger](http://www.ledger-cli.org/) fails silently instead of complaining in the following situations:
 - If the first line in a transaction begins with a space, [ledger](http://www.ledger-cli.org/) will ignore
   the whole transaction.
 - If the amount in a posting is preceded by only a single space (not by several spaces or a tab character),
   the amount is interpreted as part of the account name, and a default amount is generated. This was never
   what I wanted.

## Debits and Credits

[Ledger](http://www.ledger-cli.org/) checks that transactions balance by making sure that all the amounts posted in a transaction
add up to zero. This means that you need to use negative amounts in places where you would normally expect
to see positive amounts. For example, the transaction below tells [ledger](http://www.ledger-cli.org/) 
to *decrease* the amount in the ```Liabilities:MasterCard``` account by $10, to offset the $10 increase in the
expense account.

```
2006/10/15 Exxon
      Expenses:Auto:Gas        $10.00
      Liabilities:MasterCard  -$10.00
```
In reality (or at least the usual book-keeping conventions) an increase in a liability should balance
an equal increase in an expense account. [Describing transactions in terms of debits and credits]
(http://en.wikipedia.org/wiki/Debits_and_credits) is pointlessly complicated, but
[ledger](http://www.ledger-cli.org/)'s alternative (making the user manually negate amounts for income,
liability, and equity accounts) is confusing.

**Ledger.py** knows that income, liability and equity accounts are different to (and offset) expense and asset
accounts, which means that it understands that this transaction balances:
```
2006/10/15 Exxon
      Expenses:Auto:Gas      $10.00
      Liabilities:MasterCard $10.00
```
