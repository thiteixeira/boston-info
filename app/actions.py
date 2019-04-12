import os
import datetime
import re
from slackclient import SlackClient
from app.utils.arcgis_helpers import geocode_address, get_feature_location, get_geodesic_distance

# TODO: Add more commands
EXAMPLE_COMMAND = ['food trucks']
MENTION_REGEX = '^<@(|[WU].+?)>(.*)'

# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# TODO: Get rid of these hard-coded things
URL = "https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/" \
      "services/food_trucks_schedule/FeatureServer/0/"
QUERY = {'where': '1=1', 'out_sr': '4326'}
MILE = 1600
DAY = datetime.datetime.today().strftime('%A')


def parse_bot_commands(slack_events):
    """
    Parses a list of events coming from the Slack RTM API to find
    bot commands.
    If a bot command is found, this function returns a tuple of command
    and channel.
    If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
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
    Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(
        EXAMPLE_COMMAND[0])

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
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )
