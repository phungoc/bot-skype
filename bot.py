# -*- coding: utf-8 -*-
from skpy import SkypeEventLoop, SkypeNewMessageEvent, Skype, SkypeUser, SkypeMsg, SkypeImageMsg, SkypeChatUpdateEvent
from dateutil import relativedelta
import datetime
import time
import os
import re
import random
import json

import utils
import secret_key as key


sk = utils.init_skype()


print('Bot is running...')


class SkypePing(SkypeEventLoop):
    def onEvent(self, event):
        try:
            if isinstance(event, SkypeNewMessageEvent) and not event.msg.userId == self.userId:

                chat_id = event.msg.chatId
                user_id = event.msg.userId
                user_name = event.msg.user.name
                user_name_first = event.msg.user.name.first

                # filter space
                content = utils.filter_space(event.msg.content.lower())

                if "legacyquote" not in content and "<ss type=" not in content and "<a href=" not in content and "URIObject" not in content:

                    if content == "hi bot":
                        event.msg.chat.setTyping(active=True)
                        event.msg.chat.sendMsg(
                            "Hi " + utils.mention_user(user_id), rich=True
                        )
                        event.msg.chat.setTyping(active=False)

            # automatically accept requests
            if len(sk.contacts.requests()) > 0:
                for request in sk.contacts.requests():
                    request.accept()

        except:
            None


sk = SkypePing(tokenFile="token", autoAck=True)
sk.loop()
