import os
import datetime
import re
from slackclient import SlackClient
from app.utils.arcgis_helpers import geocode_address, get_feature_location, \
    get_geodesic_distance

# TODO: Add more commands
EXAMPLE_COMMAND = 'food trucks'
MENTION_REGEX = '^<@(|[WU].+?)>(.*)'
sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# TODO: Get rid of these hard-coded things
URL = "https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/" \
      "services/food_trucks_schedule/FeatureServer/0/"
QUERY = {'where': '1=1', 'out_sr': '4326'}
MILE = 1600
DAY = datetime.datetime.today().strftime('%A')


def parse_bot_commands(slack_events):
    """
    Iterates through a list of events from the SLACK RTM API.
    If a bot command is found, it returns a tuple, else, returns None.
    :param slack_events:
    :return: tuple with command and channel
    """
    bot_id = sc.api_call("auth.test")["user_id"]
    for event in slack_events:
        if event["type"] == "message" and "subtype" not in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == bot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
    Find mention at the beginning of the message and returns the user id
    and the message text.
    :param message_text:
    :return: user id, message
    """
    """
    Finds a direct mention (a mention that is at the beginning)
    in message text and returns the user ID which was mentioned.
    If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group
    # contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (
        None, None)


def handle_command(command, channel):
    """
    If bot command is known, handle it, else, return example
    :param command:
    :param channel:
    :return:
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
        trucks = get_feature_location(URL, QUERY)

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
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )
