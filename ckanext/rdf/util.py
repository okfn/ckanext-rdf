from time import strptime
from datetime import date, datetime
from vocab import Literal

def parse_date(value):
    try:
        strptime(value, "%Y")
        return Literal(value, datatype=XSD.gYear)
    except ValueError: pass
    try:
        strptime(value, "%Y-%m")
        return Literal(value, datatype=XSD.gYearMonth)
    except ValueError: pass
    try:
        strptime(value, "%Y-%m-%d")
        return Literal(value, datatype=XSD.date)
    except ValueError: pass
    try:
        d = strptime(value, "%d/%m/%Y")
        return Literal(date(d.tm_year, d.tm_mon, d.tm_mday))
    except ValueError: pass
    try:
        d = strptime(value, "%d/%m/%y")
        return Literal(date(d.tm_year, d.tm_mon, d.tm_mday))
    except ValueError: pass
    try:
        d = strptime(value, "%d/%m/%Y %H:%M")
        return Literal(datetime(d.tm_year, d.tm_mon, d.tm_mday, d.tm_hour, d.tm_min))
    except ValueError: pass
    try:
        d = strptime(value, "%d/%m/%y %H:%M")
        return Literal(datetime(d.tm_year, d.tm_mon, d.tm_mday, d.tm_hour, d.tm_min))
    except ValueError: pass
    return Literal(value)



