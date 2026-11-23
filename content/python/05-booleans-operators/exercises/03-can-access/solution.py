def can_access(is_admin, is_owner, is_banned):
    return (is_admin or is_owner) and not is_banned
