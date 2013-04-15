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

[Ledger](http://www.ledger-cli.org/) checks that transactions balance by making sure that the amounts
posted in a transaction add up to zero. This means that you need to use negative amounts in places where
you would expect to use positive amounts. For example, the transaction below tells
[ledger](http://www.ledger-cli.org/) to *decrease* the amount in the ```Liabilities:MasterCard```
account by $10, to offset a $10 increase in the expense account.

```
2006/10/15 Exxon
      Expenses:Auto:Gas        $10.00
      Liabilities:MasterCard  -$10.00
```

I'm probably stupid, but I found this confusing. It's not too bad when
you're concentrating, but it's easy to slip up and use the
non-standard sign to adjust an asset or expense account instead of an
income, or liability or equity account like
[ledger](http://www.ledger-cli.org/) wants you to. For example, in the
'paying for fuel with a credit-card' example, making the expense
amount the negative one has as much intuitive appeal to me, as making the
liability amount negative. How do I remember I'm not supposed to write
it this way?:
```
2006/10/15 Exxon
      Expenses:Auto:Gas      -$10.00
      Liabilities:MasterCard  $10.00
```
After all, increases in either expense or liabilities both affect net
worth negatively. How do I remember which ones I'm meant to negate? It
wouldn't be so bad if you only ever made postings to each account in
one direction, but I frequently make both negative and positive
postings to liability accounts like credit cards.

It's simpler to use the normal book-keeping conventions where an
increase in a liability will balance an equal increase in an expense
account. [Describing transactions in terms of debits and credits]
(http://en.wikipedia.org/wiki/Debits_and_credits) is pointlessly
complicated, but [ledger](http://www.ledger-cli.org/)'s simple
alternative (making the user manually negate amounts for income,
liability, and equity accounts) is confusing.

**Ledger.py** knows that income, liability and equity accounts are
different to (and offset) expense and asset accounts, which means that
it understands that this transaction balances:
```
2006/10/15 Exxon
      Expenses:Auto:Gas      $10.00
      Liabilities:MasterCard $10.00
```
