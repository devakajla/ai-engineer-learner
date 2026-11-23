class SignupService:
    def __init__(self, store, mailer):
        self.store = store
        self.mailer = mailer

    def signup(self, email):
        email = email.strip().lower()
        if email.count("@") != 1:
            raise ValueError("invalid email")
        if self.store.exists(email):
            raise ValueError("already registered")
        self.store.add(email)
        self.mailer.send(email, "Welcome!")
        return email
