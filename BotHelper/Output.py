import datetime

def output(message):
    """
    Print message with UTC timestamp
    """
    print(f"UTC: {datetime.datetime.utcnow().timestamp()} - {message}")