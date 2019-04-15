import os
import re
from slackclient import SlackClient
from app.utils.food_trucks import  food_trucks

# TODO: Add more commands
EXAMPLE_COMMAND = ['food trucks', 'farmers markets']
MENTION_REGEX = '^<@(|[WU].+?)>(.*)'
sc = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


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
    default_response = 'I don\'t know that. Try *{}* or *{}*.'.format(
        EXAMPLE_COMMAND[0], EXAMPLE_COMMAND[1])

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND[0]):
        if command == 'food trucks':
            response = food_trucks()

    # Sends the response back to the channel
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )
