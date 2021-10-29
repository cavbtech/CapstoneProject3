from datetime import datetime

## getCurrentTime return the time in expected format
## default format is "%H:%M:%S" ie HH:mi:SS format
def getCurrentTime(timeFormat="%b-%d-%Y %H:%M:%S"):
    now = datetime.now()
    current_time = now.strftime(timeFormat)
    print("Current Time =", current_time)