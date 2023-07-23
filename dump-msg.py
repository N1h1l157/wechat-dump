#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging

from lxml import etree

from wechat.parser import WeChatDBParser
from wechat.common.textutil import safe_filename
import sys, os
import xml.etree.ElementTree as ET

logger = logging.getLogger("wechat")


def is_valid_xml(xml_str):
    try:
        # 使用 lxml 解析库尝试解析数据
        etree.fromstring(xml_str)
        return True
    except etree.XMLSyntaxError:
        pass

    return False


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("Usage: {0} <path to decrypted_database.db> <output_dir>".format(sys.argv[0]))

    db_file = sys.argv[1]
    output_dir = sys.argv[2]
    try:
        os.mkdir(output_dir)
    except:
        pass
    if not os.path.isdir(output_dir):
        sys.exit("Error creating directory {}".format(output_dir))

    parser = WeChatDBParser(db_file)

    for chatid, msgs in parser.msgs_by_chat.items():
        name = parser.contacts[chatid]
        if len(name) == 0:
            logger.info(f"Chat {chatid} doesn't have a valid display name.")
            name = str(id(chatid))
        logger.info(f"Writing msgs for {name}")
        safe_name = safe_filename(name)
        outf = os.path.join(output_dir, safe_name + '.txt')
        if os.path.isfile(outf):
            logger.info(f"File {outf} exists! Skip contact {name}")
            continue

        with open(outf, 'w') as f:
            for m in msgs:
                # TODO 需要通过消息类型决定怎么存储而不是在这里存储
                try:
                    # if is_valid_xml(str(m)):
                    #     root = etree.fromstring(m)
                    #     title_element = root.find('.//title')
                    #     if title_element is not None:
                    #         title_content = title_element.text
                    #         # 将提取的 title 内容写入文件
                    #         f.write(title_content)
                    #         f.write("\n")
                    #         print(str(title_content))
                    #     else:
                    #         print(f"Chat ID: {chatid}, No title found in the XML data.")
                    # else:
                    #     # 如果不是有效的 XML 格式，则直接将 m 写入文件
                    f.write(str(m))
                    f.write("\n")
                    print(str(m))
                # TODO 未知情况，即便不是 xml 和 str 还有其他的格式
                except:
                    pass