# -*- coding: UTF-8 -*-

import sqlite3
from collections import defaultdict
import itertools
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from .msg import WeChatMsg, TYPE_SYSTEM
from .common.textutil import ensure_unicode

""" tables in concern:
emojiinfo
imginfo2
addr_upload2
chatroom
message
rcontact
"""


class WeChatDBParser(object):
    FIELDS = ["msgSvrId", "type", "isSend", "createTime", "talker", "content", "imgPath"]

    def __init__(self, db_fname):
        """ db_fname: a decrypted EnMicroMsg.db"""
        self.db_fname = db_fname  # 解密后的数据库名字
        self.db_conn = sqlite3.connect(self.db_fname)
        self.cc = self.db_conn.cursor()
        self.contacts = {}  # username -> nickname
        self.contacts_rev = defaultdict(list)
        self.msgs_by_chat = defaultdict(list)
        self.emoji_groups = {}
        self.emoji_info = {}
        self.emoji_encryption_key = None
        self._parse()

    # 获取总共有多少个名字以及自己的名字
    def _parse_contact(self):
        # 导入defaultdict来构建反向联系人字典
        from collections import defaultdict

        # 查询 rcontact 表，获取微信名，备注，以及用户名
        contacts = self.cc.execute("SELECT username, conRemark, nickname FROM rcontact")

        # 使用defaultdict构建联系人字典
        self.contacts = defaultdict(str)
        self.contacts_rev = defaultdict(list)

        for username, remark, nickname in contacts:
            name = ensure_unicode(remark) if remark else ensure_unicode(nickname)
            self.contacts[username] = name
            self.contacts_rev[name].append(username)

        logger.info(f"Found {len(self.contacts)} names in `contact` table.")

    # 获取 message 表中的 msgSvrld, 消息类型，是否发送，创建的时间戳，talker，内容以及图片路径
    def _parse_msg(self):
        msgs_tot_cnt = 0
        db_msgs = self.cc.execute(f"SELECT msgSvrId, type, isSend, createTime, talker, content, imgPath FROM message")
        for row in db_msgs:
            values = self._parse_msg_row(row)
            if not values:
                continue
            msg = WeChatMsg(values)
            # TODO keep system message?
            if not WeChatMsg.filter_type(msg.type):
                self.msgs_by_chat[msg.chat].append(msg)

        for k, v in self.msgs_by_chat.items():
            self.msgs_by_chat[k] = sorted(v, key=lambda x: x.createTime)
            msgs_tot_cnt += len(v)
        logger.info(f"Found {msgs_tot_cnt} message records.")

    # 从 userinfo 表中获取消息类型及消息的值
    def _parse_userinfo(self):
        userinfo = self.cc.execute("SELECT id, value FROM userinfo")
        userinfo_dict = dict(userinfo)
        self.username = userinfo_dict[2]
        logger.info(f"Your username is: {self.username}")

    # 从 ImgInfo2 表中获取 msgSvrld以及大图片路径
    def _parse_imginfo(self):
        imginfo2 = self.cc.execute("SELECT msgSvrId, bigImgPath FROM ImgInfo2")
        self.imginfo = {k: v for (k, v) in imginfo2 if not v.startswith('SERVERID://')}
        logger.info(f"Found {len(self.imginfo)} hd image records.")

    def _find_msg_by_type(self, msgs=None):
        ret = []
        if msgs is None:
            msgs = itertools.chain.from_iterable(self.msgs_by_chat.itervalues())
        for msg in msgs:
            if msg.type == 34:
                ret.append(msg)
        return sorted(ret)

    # 从 EmojiInfo 表中获取微信提供的表情包（原来作者提供的是EmojiInfoDesc，发现已经不可用）
    def _parse_emoji(self):
        query = self.cc.execute("SELECT md5, groupid FROM EmojiInfo")
        for md5, group in query:
            self.emoji_groups[md5] = group

        try:
            query = self.cc.execute(" SELECT md5, catalog, name, cdnUrl, encrypturl, aeskey FROM EmojiInfo")
        except:  # old database does not have cdnurl
            pass
        else:
            for md5, catalog, name, cdnUrl, encrypturl, aeskey in query:
                if cdnUrl or encrypturl:
                    self.emoji_info[md5] = (catalog, cdnUrl, encrypturl, aeskey)

    def _parse(self):
        self._parse_userinfo()
        self._parse_contact()
        self._parse_msg()
        self._parse_imginfo()
        self._parse_emoji()

    def get_emoji_encryption_key(self):
        # obtain local encryption key in a special entry in the database
        # this also equals to md5(imei)
        query = self.cc.execute("SELECT md5 FROM EmojiInfo where catalog == 153")
        results = list(query)
        if len(results):
            assert len(results) == 1, "Found > 1 encryption keys in EmojiInfo. This is a bug!"
            return results[0][0]
        return None

    # process the values in a row
    def _parse_msg_row(self, row):
        """ parse a record of message into my format"""
        values = dict(zip(WeChatDBParser.FIELDS, row))
        """
        # row 是数据库查询返回的一行记录，这个记录是一个元组或列表
        row = (12345, 1, 1, 1626789000, "user123", "Hello, this is a message.", "/path/to/image.jpg")
        
        # zip(WeChatDBParser.FIELDS, row) 将字段名列表 FIELDS 和数据库返回的记录 row 进行配对，生成一个元组的迭代器。
        ("msgSvrId", 12345),
        ("type", 1),
        ("isSend", 1),
        ("createTime", 1626789000),
        ("talker", "user123"),
        ("content", "Hello, this is a message."),
        ("imgPath", "/path/to/image.jpg")
        
        # dict() 函数将上述元组迭代器转换为一个字典 values，其中字段名为键，对应的字段值为值。
        values = {
            "msgSvrId": 12345,
            "type": 1,
            "isSend": 1,
            "createTime": 1626789000,
            "talker": "user123",
            "content": "Hello, this is a message.",
            "imgPath": "/path/to/image.jpg"
        }
        """
        # 聊天内容在content里头
        values['content'] = ensure_unicode(values['content']) if values['content'] else ''
        values['createTime'] = datetime.fromtimestamp(values['createTime'] / 1000)
        values['chat'] = values['talker']

        try:
            if values['chat'].endswith('@chatroom'):
                values['chat_nickname'] = self.contacts[values['chat']]
                content = values['content']

                if values['isSend'] == 1:
                    values['talker'] = self.username
                elif values['type'] == TYPE_SYSTEM:
                    values['talker'] = 'SYSTEM'
                else:
                    talker = content[:content.find(':')]
                    values['talker'] = talker
                    values['talker_nickname'] = self.contacts.get(talker, talker)

                values['content'] = content[content.find('\n') + 1:]
            else:
                tk_id = values['talker']
                values['chat'] = tk_id
                values['chat_nickname'] = self.contacts[tk_id]
                values['talker'] = tk_id
                values['talker_nickname'] = self.contacts[tk_id]

        except KeyError:
            # 删除联系人后，可能将消息保存在数据库中
            logger.warning(f"Unknown contact: {values.get('talker', '')}")
            return None
        return values

    @property
    # @property 是 Python 中的一个装饰器（decorator），用于将类方法转换为属性（property）
    def all_chat_ids(self):
        return self.msgs_by_chat.keys()

    @property
    def all_chat_nicknames(self):
        return [self.contacts[k] for k in self.all_chat_ids if len(self.contacts[k])]

    def get_id_by_nickname(self, nickname):
        """
        Get chat id by nickname.
        """
        l = self.contacts_rev[nickname]
        if len(l) == 0:
            raise KeyError(f"No contacts have nickname {nickname}")
        if len(l) > 1:
            logger.warning(f"More than one contacts have nickname {nickname}! Using the first contact")
        return l[0]

    def get_chat_id(self, nick_name_or_id):
        """
        Get the unique chat id by either chat id itself, or the nickname of the chat.
        """
        if nick_name_or_id in self.contacts:
            return nick_name_or_id
        else:
            return self.get_id_by_nickname(nick_name_or_id)
