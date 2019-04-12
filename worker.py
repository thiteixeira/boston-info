from app.actions import Actions
from app.utils.slackhelper import SlackHelper

'''
# Main function
def main():
    slackhelper = SlackHelper()
    actions = Actions(slackhelper)
    actions.notify_channel()


if __name__ == '__main__':
    main()
'''
import os
import time
import re
from slackclient import SlackClient
from pprint import pprint
from arcgis.gis import *
from arcgis.features import FeatureLayer
from arcgis.geocoding import geocode
from arcgis import geometry
import datetime

gis = GIS()

SLACK_BOT_TOKEN = 'xoxb-5176465338-588736110386-qRkIstpNJLhHyAves0iKnjNF'
URL = "https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/" \
      "services/food_trucks_schedule/FeatureServer/0/"
QUERY = {'where': '1=1', 'out_sr': '4326'}
DAY = datetime.datetime.today().strftime('%A')
MILE = 1600

slack_client = SlackClient(SLACK_BOT_TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "food trucks"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def get_features_from_feature_server(url, query):
    """
    Given a url to a City of Boston Feature Server, return a list
    of Features (for example, parking lots that are not full)

    :param url: url for Feature Server
    :param query: query to select features (example: "Spaces > 0")
    :return: list of all features returned from the query
    """
    # print('Received: ' + url + '\nand query: ' + str(query))
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
    m_address = m_address + ", City: Boston, State: MA"
    m_location = geocode(address=m_address)[0]
    return m_location['location']


def get_truck_location(url, query):
    return get_features_from_feature_server(url, query)


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def get_geodesic_distance(feature1, feature2):
    geometry1 = feature1  # ['geometry']
    geometry2 = feature2['geometry']
    spation_ref = {"wkid": 4326}
    return geometry.distance(spation_ref,
                             geometry1,
                             geometry2,
                             distance_unit='',
                             geodesic=True)['distance']


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned.
        If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group
    # contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (
    None, None)


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(
        EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "Here's what I found:\n"
        address = geocode_address("220 Clarendon Street")
        trucks = get_truck_location(URL, QUERY)

        trucks_today = []
        for t in trucks:
            if (t['attributes']['Day'] == DAY and
                    t['attributes']['Time'] == 'Lunch'):
                trucks_today.append(t)

        for t in trucks_today:
            distance = get_geodesic_distance(address, t)
            if distance <= MILE:
                response += (t['attributes']['Truck'] + ' is located at ' +
                             t['attributes']['Loc'] + ' between ' +
                             t['attributes']['Start_time'] + ' and ' +
                             t['attributes']['End_time'] + '\n')

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")


