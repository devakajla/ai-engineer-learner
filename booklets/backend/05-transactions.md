# 5. Transactions, ACID and locking

Think of sending 100 rupees from Asha to Ravi. The database does two things:

1. take 100 from Asha
2. add 100 to Ravi

What if the server crashes after step 1? Asha lost 100 and Ravi got nothing. Money vanished. A **transaction** fixes this: it groups steps into one unit that either **fully happens or does not happen at all**.

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;      -- make both changes permanent
-- or ROLLBACK; -- undo both
```

## ACID

Transactions promise four things, called ACID.

@@ grid 2 | Figure 5.1: the four promises.
Atomicity|all steps happen, or none;a crash in the middle leaves nothing half done|blue
Consistency|the data always follows the rules;(balance >= 0, foreign keys, unique)|green
Isolation|transactions running together;do not see each other's half-done work|yellow
Durability|once committed, it is saved;even if the power goes out|purple
@@ end

| Letter | Real life |
| --- | --- |
| **A**tomicity | An ATM gives cash **and** reduces balance, or does neither. |
| **C**onsistency | The bank never allows a state that breaks its rules. |
| **I**solation | Two people using the same account at once do not corrupt it. |
| **D**urability | After "success", a restart cannot lose your payment. |

## Why isolation is hard

Two transactions at the same time can disturb each other. These disturbances have names (called anomalies).

| Problem | What happens |
| --- | --- |
| **Dirty read** | you read data another transaction has not committed yet (it may roll back) |
| **Non-repeatable read** | you read a row twice in one transaction and get different values, because someone committed in between |
| **Phantom read** | you run the same query twice and the second time new rows appear |
| **Lost update** | two transactions read the same value, both change it, the last one overwrites the first |

**Lost update example.** A counter is `10`. Two requests each read `10`, each write `11`. Final value: `11`, but it should be `12`.

## Isolation levels

More isolation means fewer surprises, but more waiting.

| Level | Dirty read | Non-repeatable | Phantom |
| --- | --- | --- | --- |
| Read Uncommitted | possible | possible | possible |
| **Read Committed** (Postgres default) | no | possible | possible |
| Repeatable Read | no | no | no (in Postgres) |
| Serializable | no | no | no |

- **Read Committed**: each statement sees only committed data. Good for most apps.
- **Serializable**: behaves as if transactions ran one after another. Safest, but Postgres may abort one of them, and your code must **retry**.

## Locks

To avoid lost updates, you can make others wait.

**Pessimistic locking**: "I expect conflicts, so I lock first."

```sql
BEGIN;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;  -- locks this row
-- other transactions that want this row now wait
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;                                                 -- lock released
```

**Optimistic locking**: "I expect conflicts to be rare, so I do not lock. I check at the end." Add a `version` column.

```sql
UPDATE products
SET stock = 4, version = version + 1
WHERE id = 9 AND version = 3;   -- only succeeds if nobody changed it
-- -> UPDATE 1  (success)  or  UPDATE 0  (someone else changed it; reload and retry)
```

| | Pessimistic | Optimistic |
| --- | --- | --- |
| Best when | conflicts are common | conflicts are rare |
| Cost | others wait | a retry on conflict |
| Example | seat booking, money | editing a profile |

Often the simplest fix for a counter is to let the database do the math in one statement: `UPDATE t SET n = n + 1 WHERE id = 1;`. This is atomic.

## Deadlocks

Transaction A locks row 1 and wants row 2. Transaction B locks row 2 and wants row 1. Both wait forever. Postgres notices, kills one of them, and the other continues.

@@ flow | Figure 5.2: a deadlock.
Transaction A|holds row 1;wants row 2|blue <-wait for each other-> Transaction B|holds row 2;wants row 1|red
@@ end

How to avoid: always lock rows in the **same order**, and keep transactions **short**.

## Idempotency again

Retries are everywhere (clients, queues, workers). A transaction that is safe to repeat is a gift. A trick: a `UNIQUE` constraint on the request id. A second attempt fails with a duplicate error, and you treat that as "already done".

::: {.box .fastapi}
**How FastAPI does this**

In SQLAlchemy, a session wraps a transaction. With `async with session.begin():` everything inside commits together, or rolls back if an exception is raised. A common pattern is one session per request, given to your route with `Depends`. A duplicate key shows up as `IntegrityError`, and you turn it into a `409 Conflict`.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Reading a value into Python, changing it, and writing it back (`balance = row.balance - 100`). Two requests can overwrite each other. Let SQL do the math or lock the row.
- Long transactions: calling an external API or `sleep` while a transaction is open. Locks stay held and others wait.
- Forgetting to roll back after an error.
- Not retrying after a serialization failure or deadlock.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is ACID?**
Atomicity, Consistency, Isolation, Durability. Together they make a transaction all-or-nothing, rule-following, safe under concurrency and permanent.

**Q: What is the default isolation level in Postgres?**
Read Committed.

**Q: Optimistic vs pessimistic locking?**
Pessimistic locks the row first (`FOR UPDATE`) and others wait. Optimistic does not lock; it checks a version at write time and retries on conflict.

**Q: What is a deadlock and how do you avoid it?**
Two transactions each wait for a lock the other holds. Lock in a fixed order and keep transactions short.

**Q: How do you stop a lost update on a counter?**
Use an atomic `UPDATE ... SET n = n + 1`, or lock the row, or use a version column.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Two users buy the last ticket at the same moment. Describe what can go wrong without a transaction, and give two ways to prevent it.
2. Match each to an ACID letter: (a) "after a crash my paid order is still there", (b) "a balance can never go below 0", (c) "the transfer happens fully or not at all".
3. A transaction reads a row, then calls a payment API that takes 5 seconds, then writes. Why is this a problem?
4. Two `UPDATE`s: A updates rows 1 then 2, B updates rows 2 then 1. What can happen? Fix it.
5. **Think:** when would you choose Serializable and accept retries?
:::
