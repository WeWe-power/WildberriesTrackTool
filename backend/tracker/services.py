import datetime


def get_time(date, date_formats):
    date_parsed = None
    for date_format in date_formats:
        try:
            date_parsed = datetime.datetime.strptime(date, date_format).timestamp()
        except ValueError:
            continue
    return date_parsed
