# 7. Authentication and authorization

Two questions come up at every request:

1. **Authentication (authn):** *Who are you?*
2. **Authorization (authz):** *What are you allowed to do?*

Think of an office. The guard at the gate checks your ID card (authentication). Then your card opens some doors but not others (authorization).

@@ flow | Figure 7.1: authn first, then authz.
Request|comes with proof;(password, token, key)|blue -> Authentication|who is this?|green -> Authorization|may they do this?|yellow -> Action|do the work|purple
@@ end

## Passwords: never store them as they are

If your database leaks and passwords are readable, every user is in danger, because people reuse passwords. So you store a **hash**.

A **hash function** turns any text into a fixed-length scrambled value. It goes one way only: you cannot get the password back from the hash.

```
hash("hunter2") -> 9f86d081884c7d659a2feaa0c55ad015...
```

At login, you hash what the user typed and compare it with the stored hash.

Two problems with a plain hash, and their fixes:

- Two users with the same password get the same hash. Attackers use big tables of precomputed hashes. **Fix: a salt**, a random value added to each password before hashing, so every hash is different.
- Fast hashes (like SHA-256) let an attacker try billions of guesses per second. **Fix: use a slow, purpose-built password hash**: **bcrypt**, **scrypt** or **argon2**. They are slow on purpose.

> Hashing is not encryption. Encryption can be reversed with a key. A password hash cannot, which is exactly what you want.

Never write your own hashing scheme. Use a library, for example `argon2-cffi` or `passlib`.

## Sessions vs tokens

After login, the user should not send the password again on every request. The server gives them a proof of login. There are two main designs.

### Session (server remembers)

1. User logs in. The server creates a **session** (a record in Redis or the database) and gives the browser a random **session id** in a cookie.
2. On each request the browser sends the cookie. The server looks the id up to find the user.

Good: you can end any session instantly (logout, ban). Bad: every request needs a lookup in shared storage.

### Token (server remembers nothing)

The server gives the client a signed **token** that already contains who the user is. The common type is a **JWT** (JSON Web Token).

A JWT has three parts, joined by dots:

@@ flow | Figure 7.2: the three parts of a JWT.
Header|algorithm;(HS256)|blue -> Payload|claims;(user id, role, expiry)|green -> Signature|proof it was not changed|yellow
@@ end

```
eyJhbGciOi...  .  eyJzdWIiOiI3Iiwicm9sZSI6InVzZXIiLCJleHAiOjE3...  .  SflKxwRJSM...
```

The payload is only **encoded**, not secret. Anyone can read it. The **signature** (made with a secret key only the server has) stops anyone from changing it. The server checks the signature and trusts the payload. No database lookup needed.

```json
{"sub": "7", "role": "user", "exp": 1767225600}
```

`sub` is the user id. `exp` is the expiry time.

| | Session | JWT |
| --- | --- | --- |
| Server stores state | yes | no (stateless) |
| End a login instantly | easy | hard (token is valid until it expires) |
| Scale across servers | needs shared store | easy |
| Typical use | websites | APIs, mobile apps, microservices |

### Access and refresh tokens

A JWT cannot be cancelled easily, so keep it short-lived.

- **Access token**: lives 5 to 15 minutes. Sent on every request.
- **Refresh token**: lives days or weeks. Used only to get a new access token. It is stored on the server side too, so you *can* revoke it.

If an access token is stolen, it stops working in minutes. A user can log out by revoking the refresh token.

## Where to keep the token: cookie or header?

| | Cookie (HttpOnly) | `Authorization` header |
| --- | --- | --- |
| Sent automatically by browser | yes | no, your code adds it |
| Safe from XSS (script theft) | **yes** if `HttpOnly` | no, if kept in JavaScript storage |
| Needs CSRF protection | **yes** | no |
| Works well for mobile and APIs | meh | yes |

- **XSS**: an attacker injects JavaScript into your page and steals what it can read.
- **CSRF**: another site tricks the browser into sending your cookie to your API. Defend with `SameSite=Lax` or `Strict` cookies and CSRF tokens.

Good cookie flags: `HttpOnly` (script cannot read), `Secure` (HTTPS only), `SameSite`.

## OAuth2: "Login with Google"

Sometimes you do not want to handle passwords at all. **OAuth2** lets a user give your app limited access through another service.

The roles:

| Role | Example |
| --- | --- |
| Resource owner | the user |
| Client | your app |
| Authorization server | Google's login |
| Resource server | Google's API |

The common flow (authorization code):

@@ vflow | Figure 7.3: OAuth2 authorization code flow, simplified.
1. Your app|sends the user to Google's login page|blue -user logs in, says yes-> 2. Google|redirects back to your app with a short code|yellow -code-> 3. Your server|swaps the code (plus your secret) for tokens|green -tokens-> 4. Your server|reads the user's identity, creates your own session or JWT|purple
@@ end

The user's password goes only to Google, never to you. **OpenID Connect (OIDC)** adds an identity layer on top of OAuth2: it tells you *who* the user is.

> The "OAuth2 password flow" in FastAPI's docs is simpler: the user sends username and password straight to your own login endpoint, and you return a token. It is great for learning and for your own apps.

## API keys

For machine-to-machine calls, a long random string is common: `X-API-Key: sk_live_...`.

- Store only the **hash** of the key in your database. Show the key once at creation.
- Let users create several keys and revoke each.
- Add permissions and rate limits per key.

## Authorization: roles and ownership

**RBAC (role based access control)**: give users roles (`user`, `admin`) and decide what each role may do.

| Action | user | admin |
| --- | --- | --- |
| read own tasks | yes | yes |
| read all tasks | no | yes |
| delete any user | no | yes |

Roles are not enough. You also need **ownership checks**: a normal user may edit *their own* task, not someone else's.

```
GET /tasks/15      -> task 15 belongs to user 9
Logged in as user 7 -> must return 403 or 404
```

Forgetting this check is **IDOR** (Insecure Direct Object Reference). It is the number one API bug: the user just changes the number in the URL and sees other people's data.

> **Rule:** every endpoint that touches a specific record must check that the current user may touch *that* record.

## Extra: MFA and other basics

- **MFA (multi-factor authentication):** something you know (password) plus something you have (phone code). It stops most account takeovers.
- Lock or slow down after many wrong passwords.
- Do not reveal whether the email or the password was wrong. Say "invalid credentials".
- Use HTTPS everywhere.

::: {.box .fastapi}
**How FastAPI does this**

- `OAuth2PasswordBearer` reads the token from the `Authorization` header and gives it to a dependency.
- You write `get_current_user` as a dependency: decode the JWT, load the user, or raise `401`.
- Any route that adds `Depends(get_current_user)` is protected. A second dependency, `require_admin`, handles roles.
- Hashing: `passlib` or `argon2-cffi`. JWT: `PyJWT`.
- Ownership: inside the route or service, compare `task.owner_id` with `user.id` and raise `403` or `404`.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Storing plain or fast-hashed passwords.
- Putting secrets inside a JWT payload. It is readable by anyone.
- A JWT that never expires.
- Checking login but not ownership (IDOR).
- Keeping a JWT in `localStorage` when a cookie would do. Any XSS can steal it.
- Telling the attacker "email not found" vs "wrong password".
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Authentication vs authorization?**
Authentication proves who you are. Authorization decides what you may do.

**Q: How do you store passwords?**
Never as plain text. Store a salted hash made with a slow algorithm such as bcrypt or argon2.

**Q: Sessions vs JWT?**
Sessions keep state on the server and are easy to revoke. JWTs carry state in a signed token, so the server stays stateless and scales easily, but a token cannot be revoked before it expires, so keep it short-lived and use refresh tokens.

**Q: Is the JWT payload secret?**
No. It is only base64 encoded. The signature protects against changes, not against reading.

**Q: What is IDOR and how do you prevent it?**
Accessing another user's record by changing an id. Prevent it with an ownership check on every request.

**Q: 401 vs 403?**
`401`: not authenticated. `403`: authenticated but not allowed.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Why is it a bad idea to store passwords with plain SHA-256, even though it is a hash?
2. Decode in your head: a JWT payload is `{"sub": "7", "role": "admin", "exp": 1767225600}`. Can a user change `role` to `admin` in their own token? Why or why not?
3. Your access token lives 7 days and a user's phone is stolen. What is the problem, and what design fixes it?
4. A user logs in as user 7 and calls `GET /invoices/42`, which belongs to user 9, and gets it. Name the bug and the fix.
5. Compare: session cookie vs JWT in a header, for a website and for a mobile app.
6. **Think:** why does "Login with Google" avoid a whole class of password problems for you?
:::
