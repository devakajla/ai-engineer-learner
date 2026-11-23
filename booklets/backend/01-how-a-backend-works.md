# 1. How a backend works

You tap "Order" in a food app. Within a second, your order is saved, the restaurant sees it and your card is charged. The phone did not do all that alone. A **backend** did.

A backend is a program that runs on another computer, waits for requests, does the real work and sends back an answer. This chapter shows the big picture. Every later chapter zooms into one part of it.

## The three parts

Almost every app has the same three parts.

- **Client**: the thing the user touches. A phone app, a website, or another program.
- **Server (backend)**: your code. It decides what to do.
- **Database**: where data is kept safely, even when the server restarts.

@@ flow | Figure 1.1: the client asks, the server decides, the database remembers.
Client|phone or browser|blue -request-> Server|your Python code|green -query-> Database|saved data|yellow
@@ end

The client never talks to the database directly. The server stands in the middle and keeps the rules. Why? A user can change anything on their own phone, so you cannot trust the client. The server is where you check who the user is and what they may do.

## The journey of one request

When you open `api.example.com/users/7`, a lot happens before your code runs.

@@ vflow | Figure 1.2: one request, from the phone to the database and back.
Client|the app sends an HTTP request|blue -find the address (DNS)-> Internet|finds the server's IP address;the request travels there|gray -spreads the traffic-> Load balancer|picks one of many server copies|purple -passes it on-> Your server|runs your code: checks, rules, queries|green -SQL query-> Database|finds the row for user 7|yellow
@@ end

Read it top to bottom. The answer travels back the same way. Most of your work happens in the green box. The other boxes are things you configure, not write.

## What HTTP looks like

HTTP is the agreed way for clients and servers to talk, using plain text. A request has three things you should notice:

```
GET /users/7 HTTP/1.1
Host: api.example.com
Accept: application/json
```

- the **method** (`GET`: "give me data")
- the **path** (`/users/7`: "which data")
- the **headers** (extra facts, like which format the client wants)

The server replies with a **status code**, headers and a **body**:

```
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 7, "name": "Asha"}
```

`200` means success. The body is **JSON**, a plain-text format that looks like a Python dict. Almost every API speaks JSON. Chapter 2 goes deep into HTTP.

::: {.box .fastapi}
**How FastAPI does this**

FastAPI is the Python tool that listens for these requests and runs your function. You write a function for a path, and FastAPI reads the request, turns the data into Python values and turns your return value into JSON.

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id, "name": "Asha"}
```
:::

## What a backend is responsible for

A backend does more than "get and save data". This list is also the map of this booklet.

| Job | Question it answers | Chapter |
| --- | --- | --- |
| Talk HTTP | How do clients ask for things? | 2 |
| Store data | Where does data live and how do we find it fast? | 3 - 6 |
| Know the user | Who is this, and what may they do? | 7 |
| Be fast | Can we avoid repeating work? | 8 |
| Do slow work later | Can the user stop waiting? | 9 |
| Stay safe under load | What if 10,000 people arrive at once? | 10, 11 |
| Be observable and secure | When something breaks or is attacked, can we tell? | 12 |
| Stay clean | Can another person understand the code? | 13 |

## Stateless servers

A server is **stateless** when it remembers nothing about a user between two requests. Each request carries everything the server needs, for example a login token. The server forgets it right after.

Why is this good? You can run 5 copies of the server behind a load balancer, and any copy can answer any request. A copy that dies costs you nothing.

The state does not vanish. It moves to the database or to a fast store like Redis.

@@ grid 2 | Figure 1.3: stateful servers break when you add copies; stateless servers do not.
Stateful (bad for scaling)|Server A remembers "Asha is logged in";Server B does not;Request 2 lands on B: "who are you?"|red
Stateless (good)|Login token comes with every request;Any server can check it;Shared state lives in the database|green
@@ end

## Layers inside the server

Real backends do not put everything in one big function. They split the work in layers, and each layer calls only the one below it.

@@ stack | Figure 1.4: the three usual layers. Chapter 13 goes deep.
Routes|read the request, check the input, send the response|blue
Services|business rules, for example "a user cannot order twice"|green
Repositories|talk to the database and nothing else|yellow
@@ end

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- **Trusting the client.** "The app hides the delete button, so users cannot delete." They can still send the request by hand. Always check on the server.
- **Keeping state in server memory.** It works on your laptop, then breaks with two servers or after a restart.
- **Returning `200` for everything.** Use the right status code. Clients and tools depend on it.
- **Mixing database code into the route.** It is hard to test and hard to change later.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is the difference between a client and a server?**
The client asks (sends a request). The server answers (sends a response). One program can be both, for example when your backend calls another API.

**Q: Why should a server be stateless?**
So any copy can handle any request. That makes it easy to scale by adding copies and safe when one copy crashes.

**Q: Why not let the client talk to the database directly?**
You cannot trust the client. The server checks identity and rules, and it keeps database passwords secret.

**Q: What does a load balancer do?**
It spreads incoming requests over several server copies, and stops sending traffic to copies that are down.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. A user opens their profile page. Name the client, the server and the database in this story, and say what each one does.
2. Your friend says: "I hide the admin button in the app, so only admins can use admin features." What is wrong with this?
3. Your server keeps a "logged-in users" list in memory. You start a second copy of the server. Describe exactly what goes wrong for a user.
4. Why is it fine that the *client* is different for each user, but the *server rules* must be the same for everyone?
5. **Think:** an app shows "5 likes" on a post. Where should the number live: client, server memory, or database? Why?

*Answers are at the end of the booklet.*
:::
