def mask_email(email):
    local, _, domain = email.partition("@")
    return local[0] + "*" * (len(local) - 1) + "@" + domain
