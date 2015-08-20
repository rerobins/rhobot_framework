"""
Roster information for the bot.

This can be a singleton since we don't plan on joining any other rooms at the moment.
"""
import logging
from rhobot import configuration
from sleekxmpp.plugins.base import base_plugin


logger = logging.getLogger(__name__)


class RosterComponent(base_plugin):

    CHANNEL_JOINED = 'rho::joined_channel'
    PRESENCE_ONLINE = 'online:%s'
    PRESENCE_OFFLINE = 'offline:%s'

    name = 'rho_bot_roster'
    dependencies = {'xep_0045', 'rho_bot_configuration'}
    description = 'Roster Plugin'

    def plugin_init(self):
        self._channel_name = None
        self._nick = None
        self._presence_objects = dict(bot=set(), web=set(), store=set())

    def post_init(self):
        """
        Configure this module to start handling the muc issues.
        :return:
        """
        self._channel_name = configuration.get_configuration().get(configuration.MUC_SECTION_NAME,
                                                                   configuration.ROOM_KEY)
        self._nick = configuration.get_configuration().get(configuration.MUC_SECTION_NAME,
                                                           configuration.ROOM_NICK_KEY)

        self.xmpp.add_event_handler(self.xmpp['rho_bot_configuration'].CONFIGURATION_RECEIVED_EVENT, self._join_room)

    def _join_room(self, event):
        """
        Join the channel that is configured by the bot.
        :param event: ignored.
        :return:
        """
        self.xmpp['xep_0045'].joinMUC(self._channel_name, self._nick, wait=True)

        self.xmpp.add_event_handler("muc::%s::got_online" % self._channel_name,
                                    self._online_helper)

        self.xmpp.add_event_handler("muc::%s::got_offline" % self._channel_name,
                                    self._offline_helper)

    def add_message_received_listener(self, callback, ignore_self=True):
        """
        Adds a message received listener to the messages that are published to the channel.
        :param callback: callback that will be notified of new messages.
        :param ignore_self: should all of the messages that are sent by this bot ignored before giving them to the
        handler.
        :return:
        """
        if ignore_self:
            self.xmpp.add_event_handler("muc::%s::message" % self._channel_name,
                                        self._generate_callback_ignore_self(callback))
        else:
            self.xmpp.add_event_handler("muc::%s::message" % self._channel_name,
                                        callback)

    def send_message(self, body='Some Data', payload=None, thread_id=None):
        """
        Send a message to the channel.
        :param body: body of the message.
        :param payload: payload that should be appended to the message.
        :param thread_id: threadi identifier if necessary.
        :return: None
        """
        message = self.xmpp.make_message(mto=self._channel_name, mbody=body, mtype='groupchat')
        if payload:
            message.append(payload)

        if thread_id:
            message['thread'] = thread_id

        message.send()

    def _online_helper(self, presence):
        """
        Handler for online presence information.
        :param presence: presence object.
        :return:
        """
        if presence['muc']['nick'] == self._nick:
            logger.info('Self')
            self.xmpp.event(self.CHANNEL_JOINED)
        else:
            logger.info('Joined Room: %s' % presence)

            self.xmpp['xep_0030'].get_info(jid=presence['from'],
                                           node='',
                                           callback=self._info_helper)

    def _offline_helper(self, presence):
        """
        Remove the presence information, unless it is our nick, then remove all presence information.
        :param presence:
        :return:
        """
        logger.info('%s' % presence)
        from_string = str(presence['from'])
        for connections in self._presence_objects.values():
            if from_string in connections:
                connections.remove(from_string)

        logger.info('%s' % self._presence_objects)

    def _info_helper(self, info):
        """
        Figure out how to categorize the objects.
        :param info:
        :return:
        """
        logger.info('Joined Room (Info): %s' % info['disco_info']['identities'])

        identities = info['disco_info']['identities']

        for key in self._presence_objects.keys():
            for _idents in identities:
                if key in _idents:
                    self._presence_objects[key].add(str(info['from']))
                    self.xmpp.event(self.PRESENCE_ONLINE % key, info['from'])

        logger.info('Received: %s' % self._presence_objects)

    def _generate_callback_ignore_self(self, callback):
        """
        Generate a callback that will be used in order to ignore all of the echo messages.
        :param callback: callback that will be notified if the message is not sent by this bot.
        :return:
        """
        def new_callback(message):

            if message['mucnick'] != self._nick:
                callback(message)

        return new_callback

rho_bot_roster = RosterComponent
