from arcgis.gis import *
from arcgis.features import FeatureLayer
from arcgis.geocoding import geocode
from arcgis import geometry

gis = GIS()


def get_features_from_feature_server(url, query):
    """
    Given a url to a Feature Server, return a list
    of Features (for example, parking lots that are not full)

    :param url: url for Feature Server
    :param query: query to select features
                  example: {'where': '1=1', 'out_sr': '4326'}
    :return: list of all features returned from the query
    """
    features = []
    f = FeatureLayer(url=url)
    feature_set = f.query(**query)
    for feature in feature_set:
        features.append(feature.as_dict)
    return features


def geocode_address(m_address):
    """
    :param m_address: address of interest in street form
    :return: address in coordinate (X and Y) form
    """
    # TODO: Make it generic to handle more cities
    m_address = m_address + ", City: Boston, State: MA"
    m_location = geocode(address=m_address)[0]
    return m_location['location']


def get_geodesic_distance(feature1, feature2):
    geometry1 = feature1['geometry']
    geometry2 = feature2['geometry']
    spation_ref = {"wkid": 4326}
    return geometry.distance(spation_ref,
                             geometry1,
                             geometry2,
                             distance_unit='',
                             geodesic=True)['distance']


def get_feature_location(url, query):
    return get_features_from_feature_server(url, query)


def get_coordinates_for_address(address):
    """
    Populates the GPS coordinates for the provided address

    :param address: address to query
    :return: a tuple of the form (lat, long)

    """
    coordinates = geocode_address(address)
    _lat = "{:.2f}".format(float(coordinates['y']))
    _long = "{:.2f}".format(float(coordinates['x']))
    return _lat, _long
