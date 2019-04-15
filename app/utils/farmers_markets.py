from app.utils.datetime_utils import get_day
from app.utils.arcgis_helpers import get_feature_location

BASE_URL = 'https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/' \
           'services/Farmers_Markets_Fresh_Trucks_View/FeatureServer/0'
QUERY = {'where': '1=1', 'out_sr': '4326'}
DAY = get_day()


def farmers_markets():
    markets = get_feature_location(BASE_URL, QUERY)
    markets_today = []
    for m in markets:
        if m not in markets_today and \
                m['attributes']['Day_of_Week'] == DAY:
            markets_today.append(m)

    response = 'Available farmers markets today are:\n'
    for m in markets_today:
        response += '*' + m['attributes']['Name'] + '* located at ' + \
                    m['attributes']['Address'] + ' from ' + \
                    m['attributes']['Hours'] + '.\n'
    return response
