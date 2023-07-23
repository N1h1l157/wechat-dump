# -*- coding: UTF-8 -*-

import base64
from pyquery import PyQuery
import logging
import json
logger = logging.getLogger(__name__)

from libchat.libchat import SqliteLibChat, ChatMsg
from .msg import *
from .common.timer import timing
from .common.progress import ProgressReporter

class LibChatHelper(object):
    """ Build LibChat messages from WeChat Msg"""

    """ Types of message whose contents are fully parsed.
        No need to save extra data for them. """
    FullyParsed = [TYPE_MSG, TYPE_SPEAK, TYPE_EMOJI,
                    TYPE_CUSTOM_EMOJI, TYPE_IMG]

    def __init__(self, parser, res):
        """ res: a 'Resource' instance
            parser: a 'WeChatDBParser' instance
        """
        self.parser = parser
        self.res = res

    def _get_image(self, msg):
        """ get image content and type from a message"""
        if msg.type == TYPE_IMG:
            # imgPath was original THUMBNAIL_DIRPATH://th_xxxxxxxxx
            imgpath = msg.imgPath.split('_')[-1]
            if not imgpath:
                logger.warning(
                    'No imgpath in an image message. Perhaps a bug in wechat: {}'.format(msg))
                return '', ''
            bigimgpath = self.parser.imginfo.get(msg.msgSvrId)
            img = self.res.get_img([imgpath, bigimgpath])
            if not img:
                logger.warning("No image found for {}".format(imgpath))
            return img, 'jpeg'
        elif msg.type == TYPE_EMOJI:
            md5 = msg.imgPath
            if md5:
                emoji_img, format = self.res.get_emoji_by_md5(md5)
                return emoji_img, format
            else:
                return '', ''
        elif msg.type == TYPE_CUSTOM_EMOJI:
            pq = PyQuery(msg.content)
            md5 = pq('emoticonmd5').text()
            if md5:
                img, format = self.res.get_emoji(md5, None)
                return img, format
            else:
                return '', ''
        else:
            return '', ''

    def _get_sound(self, msg):
        if msg.type == TYPE_SPEAK:
            audio_str, duration = self.res.get_voice_mp3(msg.imgPath)
            return base64.b64decode(audio_str)
        return b''

    def _get_extra(self, msg):
        ret = {}
        ret['type'] = msg.type
        if msg.type not in LibChatHelper.FullyParsed:
            ret['content'] = msg.content
        return json.dumps(ret)

    def _convert_msg(self, msg):
        sender = 'me' if msg.isSend else msg.talker
        chatroom = msg.get_chatroom()
        text = msg.content if msg.type == TYPE_MSG else ''
        img, format = self._get_image(msg)
        if img:
            # TODO don't use b64, directly return image content
            img = base64.b64decode(img)
        # TODO do we need to save format or voice duration?
        sound = self._get_sound(msg)
        extra = self._get_extra(msg)

        self.prgs.trigger()
        return ChatMsg(
            'wechat', msg.createTime, sender, chatroom,
            text, img, sound, extra)

    def convert_msgs(self, msgs):
        self.prgs = ProgressReporter("Parse Messages", total=len(msgs))
        ret = [self._convert_msg(m) for m in msgs]
        self.prgs.finish()
        return ret
