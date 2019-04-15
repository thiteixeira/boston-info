from app.utils.datetime_utils import get_day
from app.utils.arcgis_helpers import geocode_address, get_feature_location, \
    get_geodesic_distance

URL = "https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/" \
      "services/food_trucks_schedule/FeatureServer/0/"
QUERY = {'where': '1=1', 'out_sr': '4326'}
MILE = 1600
DAY = get_day()


def food_trucks():
    response = "Here's what I found:\n"
    address = geocode_address("220 Clarendon Street")
    trucks = get_feature_location(URL, QUERY)

    trucks_today = []
    for t in trucks:
        if (t['attributes']['Day'] == DAY and
                t['attributes']['Time'] == 'Lunch'):
            trucks_today.append(t)

    for t in trucks_today:
        distance = get_geodesic_distance(address, t)
        if distance <= MILE:
            response += (
                    '*' + t['attributes']['Truck'] + '* is located at ' +
                    t['attributes']['Loc'] + ', between ' +
                    t['attributes']['Start_time'] + ' and ' +
                    t['attributes']['End_time'] + '\n')
    return response
