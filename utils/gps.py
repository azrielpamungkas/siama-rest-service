from math import radians, cos, sin, asin, sqrt
from geopy.geocoders import Nominatim


def detector(geo):
    try:
        geolocator = Nominatim(user_agent="coordinateconverter")
        return geolocator.reverse(geo).address
    except:
        return "Antah Berantah"


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def validation(lat, lng):
    lat1 = -6.990244896200767
    lon1 = 110.42050151945978
    lat2 = float(lat)
    lon2 = float(lng)

    radius = 0.075  # in kilometer

    position = haversine(lon1, lat1, lon2, lat2)
    if position <= radius:
        return True
    return False
