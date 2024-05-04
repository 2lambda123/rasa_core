# -*- coding: utf-8 -*-

import datetime
import json
import logging
import requests
from sanic import Blueprint, response
from sanic.request import Request
from typing import Text, Dict, Any

from rasa.core.channels.channel import UserMessage, OutputChannel, InputChannel

logger = logging.getLogger(__name__)

MICROSOFT_OAUTH2_URL = 'https://login.microsoftonline.com'

MICROSOFT_OAUTH2_PATH = 'botframework.com/oauth2/v2.0/token'


class BotFramework(OutputChannel):
    """A Microsoft Bot Framework communication channel."""

    token_expiration_date = datetime.datetime.now()

    headers = None

    @classmethod
    def name(cls):
        """This function returns the string "botframework".
        Parameters:
            - cls (str): The name of the class.
        Returns:
            - str: The string "botframework".
        Processing Logic:
            - Return a string.
            - The string is "botframework".
            - The string is always the same.
            - No other parameters are needed."""
        
        return "botframework"

    def __init__(self,
                 app_id: Text,
                 app_password: Text,
                 conversation: Dict[Text, Any],
                 bot_id: Text,
                 service_url: Text) -> None:
        """Initializes the Microsoft Bot Framework Connector with the given app ID, app password, conversation dictionary, bot ID, and service URL.
        Parameters:
            - app_id (Text): The app ID for the bot.
            - app_password (Text): The app password for the bot.
            - conversation (Dict[Text, Any]): A dictionary containing information about the conversation.
            - bot_id (Text): The ID of the bot.
            - service_url (Text): The URL of the bot's service.
        Returns:
            - None: This function does not return anything.
        Processing Logic:
            - Initializes the Microsoft Bot Framework Connector.
            - Sets the app ID, app password, conversation dictionary, global URI, and bot ID.
            - Uses the service URL to create the global URI.
            - Does not return any values."""
        

        self.app_id = app_id
        self.app_password = app_password
        self.conversation = conversation
        self.global_uri = "{}v3/".format(service_url)
        self.bot_id = bot_id

    async def _get_headers(self):
        """Get headers for BotFramework API requests.
        Parameters:
            - self (BotFramework): BotFramework object.
        Returns:
            - headers (dict): Dictionary containing the necessary headers for BotFramework API requests.
        Processing Logic:
            - If token expiration date is less than current date and time:
                - Create URI using MICROSOFT_OAUTH2_URL and MICROSOFT_OAUTH2_PATH.
                - Set grant_type to 'client_credentials'.
                - Set scope to 'https://api.botframework.com/.default'.
                - Create payload dictionary with client_id, client_secret, grant_type, and scope.
                - Send POST request to URI with payload and timeout of 60 seconds.
                - If request is successful:
                    - Get access token and expiration time from response.
                    - Set token_expiration_date to current date and time plus expiration time.
                    - Create headers dictionary with content-type and Authorization.
                    - Return headers dictionary.
                - Else:
                    - Log error message.
            - Else:
                - Return headers dictionary."""
        
        if BotFramework.token_expiration_date < datetime.datetime.now():
            uri = "{}/{}".format(MICROSOFT_OAUTH2_URL, MICROSOFT_OAUTH2_PATH)
            grant_type = 'client_credentials'
            scope = 'https://api.botframework.com/.default'
            payload = {'client_id': self.app_id,
                       'client_secret': self.app_password,
                       'grant_type': grant_type,
                       'scope': scope}

            token_response = requests.post(uri, data=payload, timeout=60)

            if token_response.ok:
                token_data = token_response.json()
                access_token = token_data['access_token']
                token_expiration = token_data['expires_in']

                BotFramework.token_expiration_date = \
                    datetime.datetime.now() + \
                    datetime.timedelta(seconds=int(token_expiration))

                BotFramework.headers = {"content-type": "application/json",
                                        "Authorization": "Bearer %s" %
                                                         access_token}
                return BotFramework.headers
            else:
                logger.error('Could not get BotFramework token')
        else:
            return BotFramework.headers

    async def send(self,
                   recipient_id: Text,
                   message_data: Dict[Text, Any]) -> None:
        """Sends a message to a specific recipient using the botframework API.
        Parameters:
            - recipient_id (str): The ID of the recipient to send the message to.
            - message_data (dict): A dictionary containing the message data to be sent.
        Returns:
            - None: This function does not return any value.
        Processing Logic:
            - Constructs the API endpoint for sending messages.
            - Updates the message data with the recipient ID and bot ID.
            - Sets the notification alert to true.
            - Sends a POST request to the API endpoint with the message data.
            - Logs an error if the request is not successful."""
        

        post_message_uri = ('{}conversations/{}/activities'
                            ''.format(self.global_uri, self.conversation['id']))
        data = {"type": "message",
                "recipient": {
                    "id": recipient_id
                },
                "from": self.bot_id,
                "channelData": {
                    "notification": {
                        "alert": "true"
                    }
                },
                "text": ""}

        data.update(message_data)
        headers = await self._get_headers()
        send_response = requests.post(post_message_uri,
                                      headers=headers,
                                      data=json.dumps(data), timeout=60)

        if not send_response.ok:
            logger.error("Error trying to send botframework messge. "
                         "Response: %s", send_response.text)

    async def send_text_message(self, recipient_id, message):
        """Sends a text message to a recipient.
        Parameters:
            - recipient_id (str): The ID of the recipient.
            - message (str): The message to be sent.
        Returns:
            - None: This function does not return anything.
        Processing Logic:
            - Split message by double line breaks.
            - Create a dictionary with the message as the value for the "text" key.
            - Send the message to the recipient using the send() function."""
        
        for message_part in message.split("\n\n"):
            text_message = {"text": message_part}
            await self.send(recipient_id, text_message)

    async def send_image_url(self, recipient_id, image_url):
        """Sends an image message to a specified recipient.
        Parameters:
            - recipient_id (str): The ID of the recipient.
            - image_url (str): The URL of the image to be sent.
        Returns:
            - None: The function does not return anything.
        Processing Logic:
            - Create a hero content dictionary.
            - Add the image URL to the dictionary.
            - Create an image message dictionary.
            - Add the hero content dictionary to the image message dictionary.
            - Send the image message to the recipient.
        Example:
            await send_image_url('12345', 'https://example.com/image.jpg')"""
        
        hero_content = {
            'contentType': 'application/vnd.microsoft.card.hero',
            'content': {
                'images': [{'url': image_url}]
            }
        }

        image_message = {"attachments": [hero_content]}
        await self.send(recipient_id, image_message)

    async def send_text_with_buttons(self, recipient_id, message, buttons,
                                     **kwargs):
        """Sends a text message with buttons to a specified recipient.
        Parameters:
            - recipient_id (str): The ID of the recipient to send the message to.
            - message (str): The text message to be sent.
            - buttons (list): A list of buttons to be included in the message.
            - **kwargs: Additional keyword arguments that can be passed to the send function.
        Returns:
            - None: This function does not return any value.
        Processing Logic:
            - Creates a hero content object with the message and buttons.
            - Creates a buttons message object with the hero content.
            - Sends the buttons message to the specified recipient.
        Example:
            send_text_with_buttons("12345", "Hello!", ["Button 1", "Button 2"])
            # Sends a message with the text "Hello!" and two buttons to the recipient with ID "12345"."""
        
        hero_content = {
            'contentType': 'application/vnd.microsoft.card.hero',
            'content': {
                'subtitle': message,
                'buttons': buttons
            }
        }

        buttons_message = {"attachments": [hero_content]}
        await self.send(recipient_id, buttons_message)

    async def send_custom_message(self, recipient_id, elements):
        """Sends a custom message to a specified recipient ID.
        Parameters:
            - recipient_id (str): The ID of the recipient.
            - elements (list): A list of elements to be sent.
        Returns:
            - None: The function does not return anything.
        Processing Logic:
            - Extract the first element from the list.
            - Use the extracted element as the message to be sent.
            - Use the recipient ID to send the message.
            - The function uses asynchronous processing."""
        
        await self.send(recipient_id, elements[0])


class BotFrameworkInput(InputChannel):
    """Bot Framework input channel implementation."""

    @classmethod
    def name(cls):
        """"""
        
        return "botframework"

    @classmethod
    def from_credentials(cls, credentials):
        """"Creates an instance of the class using the provided credentials. If no credentials are provided, an exception is raised.
        Parameters:
            - credentials (dict): A dictionary containing the app_id and app_password for authentication.
        Returns:
            - Instance of the class: An instance of the class with the provided credentials.
        Processing Logic:
            - Raises exception if no credentials are provided.
            - Uses the app_id and app_password from the credentials dictionary.
            - Returns an instance of the class using the provided credentials.""""
        
        if not credentials:
            cls.raise_missing_credentials_exception()

        return cls(credentials.get("app_id"), credentials.get("app_password"))

    def __init__(self, app_id: Text, app_password: Text) -> None:
        """Create a Bot Framework input channel.

        Args:
            app_id: Bot Framework's API id
            app_password: Bot Framework application secret
        """

        self.app_id = app_id
        self.app_password = app_password

    def blueprint(self, on_new_message):
        """This function creates a Blueprint for a botframework webhook, which handles incoming messages and sends them to the specified on_new_message function. It takes in two parameters: self, which refers to the current instance of the class, and on_new_message, which is the function that will handle the incoming messages. It returns a botframework_webhook Blueprint.
        Processing Logic:
            - Creates a Blueprint for a botframework webhook.
            - Handles incoming messages and sends them to the on_new_message function.
            - Takes in two parameters: self and on_new_message.
            - Returns a botframework_webhook Blueprint."""
        

        botframework_webhook = Blueprint('botframework_webhook', __name__)

        @botframework_webhook.route("/", methods=['GET'])
        async def health(request):
            return response.json({"status": "ok"})

        @botframework_webhook.route("/webhook", methods=['POST'])
        async def webhook(request: Request):
            postdata = request.json

            try:
                if postdata["type"] == "message":
                    out_channel = BotFramework(self.app_id, self.app_password,
                                               postdata["conversation"],
                                               postdata["recipient"],
                                               postdata["serviceUrl"])

                    user_msg = UserMessage(postdata["text"], out_channel,
                                           postdata["from"]["id"],
                                           input_channel=self.name())
                    await on_new_message(user_msg)
                else:
                    logger.info("Not received message type")
            except Exception as e:
                logger.error("Exception when trying to handle "
                             "message.{0}".format(e))
                logger.debug(e, exc_info=True)
                pass

            return response.text("success")

        return botframework_webhook
