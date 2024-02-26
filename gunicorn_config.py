# Number of worker processes
workers = 4

# The address and port on which your application will listen
bind = "0.0.0.0:8000"

# Automatically reload the server when code changes (development mode)
reload = True

# The maximum number of requests a worker will process before restarting
max_requests = 1000

# The maximum number of requests a worker will process before gracefully exiting
max_requests_jitter = 100

# Log files
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log errors to stdout