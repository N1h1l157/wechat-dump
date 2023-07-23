'''
name: modify_html.py
data: 2023/07/23
feature: modify html from input file
'''

import os
import sys
import argparse
import subprocess

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--nickname', help='当前要修改的聊天记录的微信备注名')
    parser.add_argument('--input', help='要操作的html界面')
    args = parser.parse_args()
    return args

def remove_html_segment(input_file, output_file, nickname):
    # 读取原始的 HTML 文件内容
    with open(input_file, "r", encoding="utf-8") as file:
        original_content = file.read()

    # 定义要替换的 HTML 代码段
    pattern_up = f'''        </div>
      </div>
    </div>
  </div>
</body>
</html>

<html>
<head>
  <meta http-equiv="Content-Type" content="text/html;charset=utf8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <title>Chat with {nickname}</title>'''

    pattern_down = f'''</head>

<body>
  <div id="chat" class="chatPanel normalPanel">
    <div class="chatMainPanel" id="chatMainPanel">
      <div class="chatTitle">
        <div class="chatNameWrap">
          <p class="chatName" id="messagePanelTitle">{nickname}</p>
        </div>
      </div>
      <div class="chatScorll" style="position: relative; font-family:initial;">
        <div id="chat_chatmsglist" class="chatContent" style="position: absolute;">'''
        
    # 使用字符串的 replace() 方法替换，将指定的 HTML 代码段替换为空字符串
    processed_content_up = original_content.replace(pattern_up, '')
    processed_content_down = processed_content_up.replace(pattern_down, '')
    
    # 将处理后的内容写入新的文件
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(processed_content_down)
            
    
def insert_html_segment(input_file, output_file, nickname):
    # 读取原始的 HTML 文件内容
    with open(input_file, "r", encoding="utf-8") as file:
        original_content = file.read()
        
    # 定义要增加的 HTML 代码段
    pattern_insert = f'''</head>

<body>
  <div id="chat" class="chatPanel normalPanel">
    <div class="chatMainPanel" id="chatMainPanel">
      <div class="chatTitle">
        <div class="chatNameWrap">
          <p class="chatName" id="messagePanelTitle">{nickname}</p>
        </div>
      </div>
      <div class="chatScorll" style="position: relative; font-family:initial;">
        <div id="chat_chatmsglist" class="chatContent" style="position: absolute;">'''
    
    # 按行分割原始内容，并取前 89 行和 后89行 的内容进行处理
    lines = original_content.splitlines()
    processed_lines_up = lines[:89]
    processed_lines_down = lines[89:]
    
    # 将处理后的行内容拼接为字符串
    processed_content_up = "\n".join(processed_lines_up)
    processed_content_down = "\n".join(processed_lines_down)
    
    # 插入 HTML 代码片段
    processed_content_insert = processed_content_up + pattern_insert + processed_content_down
    
    # 将处理后的内容写入新的文件
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(processed_content_insert)    


def move_and_remove_files(nickname):
  
    # 执行 mv 命令，将 temp2.html 改名
    subprocess.run(["mv", "temp2.html", f"{nickname}.html"])
    
    # 执行 rm 命令，删除所有以 temp 开头且以 .html 结尾的文件
    subprocess.run(["rm", "-f", "temp1.html"]) 
    
    
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("nickname要和自己给的备注一模一样，不然会出现多个滚动条")
        print("exapmle: python modify_html.py --nickname 一个人类 --input 一个人类.html")
        print("exapmle: python modify_html.py --nickname '神棍 小明 ISFJ' --input ~/Personal/myself/微信数据库/wechat_dump/result/小明/小明.html")
        
    else:
        args = get_args()
        nickname = args.nickname
        input_html = args.input
        
        output_file1 = "temp1.html"
        output_file2 = "temp2.html"
        
        remove_html_segment(input_html, output_file1, nickname)
        insert_html_segment(output_file1, output_file2, nickname)
        move_and_remove_files(nickname)
        
        print(f"HTML 文件处理完成，并保存为 {nickname}.html。")
