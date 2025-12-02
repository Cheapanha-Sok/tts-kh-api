from urllib.parse import quote_plus

# Original password
password = "P@ssw0rd@168"

# Encode the password
encoded_password = quote_plus(password)

# Alembic requires '%%' to escape '%'
alembic_safe_password = encoded_password.replace('%', '%%')
print(f"Encoded password: {encoded_password}")
print(f"Encoded password alembic : {alembic_safe_password}")
# Now, use `alembic_safe_password` in your SQLAlchemy URL in the alembic.ini file