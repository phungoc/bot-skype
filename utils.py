from skpy import Skype, SkypeUser, SkypeMsg, SkypeChat, SkypeConnection, SkypeUtils
import os
import re
import datetime
import pytz
import dateutil.parser
import time
import random
import json
import requests

import secret_key as key


def init_skype():
    return Skype(key.USER_NAME, key.PASSWORD, "token")


# override to send audio
def sendFile(chat, content, name, image=False, audio=False, video=False):
    """
        Upload a file to the conversation.  Content should be an ASCII or binary file-like object.

        If an image, Skype will generate a thumbnail and link to the full image.

        Args:
            content (file): file-like object to retrieve the attachment's body
            name (str): filename displayed to other clients
            image (bool): whether to treat the file as an image

        Returns:
            .SkypeFileMsg: copy of the sent message object
        """
    meta = {"type": "pish/image" if image else "sharing/audio" if audio else "sharing/thumbnail" if video else "sharing/file",
            "permissions": dict(("8:{0}".format(id), ["read"]) for id in chat.userIds)}
    if not image:
        meta["filename"] = name
    objId = chat.skype.conn("POST", "https://api.asm.skype.com/v1/objects",
                            auth=SkypeConnection.Auth.Authorize,
                            headers={"X-Client-Version": "0/0.0.0.0"},
                            json=meta).json()["id"]
    objType = "imgpsh" if image else "audio" if audio else "thumbnail" if video else "original"
    urlFull = "https://api.asm.skype.com/v1/objects/{0}".format(objId)
    chat.skype.conn("PUT", "{0}/content/{1}".format(urlFull, objType),
                    auth=SkypeConnection.Auth.Authorize, data=content.read())
    size = content.tell()
    if image:
        viewLink = SkypeMsg.link(
            "https://api.asm.skype.com/s/i?{0}".format(objId))
        body = SkypeMsg.uriObject("""{0}<meta type="photo" originalName="{1}"/>""".format(viewLink, name),
                                  "Picture.1", urlFull, thumb="{0}/views/imgt1".format(urlFull), OriginalName=name)

    elif audio:
        viewLink = SkypeMsg.link(
            "https://api.asm.skype.com/s/i?{0}".format(objId))
        body = SkypeMsg.uriObject("""{0}<meta type="audio" originalName="{1}"/>""".format(viewLink, name),
                                  "Audio.1", urlFull, thumb="{0}/views/audio".format(urlFull), OriginalName=name, FileSize=size)

    elif video:
        viewLink = SkypeMsg.link(
            "https://api.asm.skype.com/s/i?{0}".format(objId))
        body = SkypeMsg.uriObject("""{0}<meta type="thumbnail" originalName="{1}"/>""".format(viewLink, name),
                                  "Video.1", urlFull, thumb="{0}/views/thumbnail".format(urlFull), OriginalName=name)

        '<URIObject uri="https://api.asm.skype.com/v1/objects/0-sa-d4-e01544ace97171317e4aee20c8f52906" url_thumbnail="https://api.asm.skype.com/v1/objects/0-sa-d4-e01544ace97171317e4aee20c8f52906/views/thumbnail" type="Video.1" doc_id="0-sa-d4-e01544ace97171317e4aee20c8f52906" width="1920" height="1080">To view this shared video, go to: <a href="https://login.skype.com/login/sso?go=webclient.xmm&amp;docid=0-sa-d4-e01544ace97171317e4aee20c8f52906">https://login.skype.com/login/sso?go=webclient.xmm&amp;docid=0-sa-d4-e01544ace97171317e4aee20c8f52906</a><OriginalName v="VID_20191030_085934.mp4"></OriginalName><FileSize v="1829526"></FileSize></URIObject>'
        '<URIObject uri="https://api.asm.skype.com/v1/objects/0-sa-d7-1eaeef19e262fb4566d84918822f99cc" url_thumbnail="https://api.asm.skype.com/v1/objects/0-sa-d7-1eaeef19e262fb4566d84918822f99cc/views/thumbnail" type="Video.1" doc_id="0-sa-d7-1eaeef19e262fb4566d84918822f99cc" width="1920" height="1080">To view this shared video, go to: <a href="https://login.skype.com/login/sso?go=webclient.xmm&amp;docid=0-sa-d7-1eaeef19e262fb4566d84918822f99cc">https://login.skype.com/login/sso?go=webclient.xmm&amp;docid=0-sa-d7-1eaeef19e262fb4566d84918822f99cc</a><OriginalName v="VID_20191030_085934.mp4"></OriginalName><FileSize v="1829526"></FileSize></URIObject>'

    else:
        viewLink = SkypeMsg.link(
            "https://login.skype.com/login/sso?go=webclient.xmm&docid={0}".format(objId))
        body = SkypeMsg.uriObject(viewLink, "File.1", urlFull, "{0}/views/thumbnail".format(urlFull), name, name,
                                  OriginalName=name, FileSize=size)
    msgType = "RichText/{0}".format(
        "UriObject" if image else "Media_GenericFile")

    return chat.sendRaw(content=body, messagetype=msgType)


def filter_space(text):
    # return " ".join(text.split())
    return re.sub(re.compile(r'\s+'), " ", text).strip()


def mention_user(id):
    user_info = render_user(id)
    user_mention = SkypeMsg.mention(user_info)
    return user_mention


def render_user(id):
    if 'name' in sk.contacts[id].raw:
        first_name = sk.contacts[id].raw['name']['first']
    if 'firstname' in sk.contacts[id].raw:
        first_name = sk.contacts[id].raw['firstname']

    user = SkypeUser(id=id, name=SkypeUser.Name(first=first_name))

    return user


def render_chat(id):
    chat_id = "8:" + id
    return SkypeChat(id=chat_id)


def generate_emoticon(name):
    return '<ss type="{}">({})</ss>'.format(name, name)


def generate_bold(text):
    return '<b raw_pre="*" raw_post="*">{0}</b>'.format(text)


sk = init_skype()
