# Configuration file for constants

EMAIL = "exceptiondecoded@gmail.com"  # Replace with your email
PASSWORD = "xxxx"
IMAP_SERVER = "imap.gmail.com"  # Replace with your IMAP server (e.g., imap.gmail.com)
CHECK_INTERVAL = 600  # Check interval in seconds

# DATABASE_CONFIG = {
#     "dbname": "my_blog",
#     "user": "admin",
#     "password": "password",
#     "host": "localhost",
#     "port": 5432,
# }

DATABASE_CONFIG = {
    "dbname": "my_blog",
    "user": "admin",
    "password": "password",
    "host": "host.docker.internal",
    "port": 5432,
}

TABLE_NAME = "ideas.posts"
