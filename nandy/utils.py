"""Common convenience functions."""

import datetime


def get_date_interval():
    """Get date interval starting with today and ending tomorrow.

    :returns: Tuple of datetimes (start, end)
    """
    start = datetime.datetime.utcnow()
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(days=1)
    return (start, end)


def get_now():
    """Get now as a utc now datetime.

    :returns: datetime
    """
    return datetime.datetime.utcnow()


def date_from_string(s):
    """Get datetime from string.

    :param s: String in format YYYY-mm-dd
    :returns: Datetime
    """
    return datetime.datetime.strptime(s, '%Y-%m-%d')
