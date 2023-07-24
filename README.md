
### 效果图展示

1）wechat-backup 导出

<img src="http://n1h1l157.github.io/N1h1l157/Safe/image-119.png" width="720" alt="Image">

2）wechat-dump 导出

<img src="http://n1h1l157.github.io/N1h1l157/Safe/image-130.png" width="470" alt="Image">

3）聊天记录转pdf

<img src="http://n1h1l157.github.io/N1h1l157/Safe/image-133.png" width="520" alt="Image">

---

### 使用流程

1）手机聊天记录备份至开启 root 的安卓模拟器

**手机聊天记录备份至电脑 -> 电脑聊天记录备份至模拟器 -> 雷电模拟器开启 root -> 模拟器下载 ES 文件浏览器并启用 root 工具箱 -> 复制微信数据库等资料到共享文件** 

2）收集以下文件夹及数据库

**auth_info_key_prefs.xml，image2，voice2，voide，avatar，Download，emoji，EnMicroMsg.db，WxFileIndex.db**

3） 解密数据库

**读取 UIN -> 与 IMEI 拼接 -> md5 加密 -> 取前 7 位即为数据库密码 -> sqlcipher导出无密码数据库**

4） 解码音频文件

**docker run --rm -v /root/voice2:/media  greycodee/silkv3-decoder**

5）运行程序解析聊天记录

---

### 程序运行命令

```shell
# 列出联系人及其微信号 
python list-chats.py ～/230721_backup/EnMicroMsg_230721.db > list_chats_23.txt

# 导出数据库中的聊天记录
python dump-msg.py ～/230721_backup/EnMicroMsg_230721.db result/msg

# 导出为 html
python dump-html.py --db ～/220921_backup/EnMicroMsg_220921.db --res ～/230721_backup --output result/Camile/Camile.html wxid_qxxxxxxx22
```

---

### 参考项目

详细流程：[http://n1h1l157.github.io/2023/07/23/SAFE/](http://n1h1l157.github.io/2023/07/23/SAFE/%E8%BD%AC%E5%82%A8%E5%BE%AE%E4%BF%A1%E8%81%8A%E5%A4%A9%E8%AE%B0%E5%BD%95/)

wechat-backup:[https://github.com/greycodee/wechat-backup](https://github.com/greycodee/wechat-backup)

wechat-dump: [https://github.com/ppwwyyxx/wechat-dump](https://github.com/ppwwyyxx/wechat-dump)

puppeteer: [https://github.com/puppeteer/puppeteer](https://github.com/puppeteer/puppeteer)

