import datetime

def get_current_datetime() -> str:
    """
    Returns the current date, day of the week, and time.
    Use this tool whenever the user asks for the current date, day, or time.
    """
    now = datetime.datetime.now()
    return now.strftime("현재 날짜: %Y년 %m월 %d일, %A, 시간: %H시 %M분 %S초")
