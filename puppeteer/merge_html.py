'''
name: merge_html.py
data: 2023/07/23
feature: merge html from folder path
'''

import os
import sys
from natsort import natsorted

def read_file(file_path):
	with open(file_path, "r", encoding="utf-8") as f:
		return f.read()

def write_file(file_path, content):
	with open(file_path, "w", encoding="utf-8") as f:
		f.write(content)

def merge_html_files(folder_path, merge_html):
	# 获取HTML文件列表并按照文件名顺序排序
	input_files = [file for file in os.listdir(folder_path) if file.endswith(".html")]
	input_files = natsorted(input_files)
	print(input_files)
	
	# 合并HTML文件
	merged_content = ""
	for file_name in input_files:
		file_path = os.path.join(folder_path, file_name)
		content = read_file(file_path)
		merged_content += content + "\n"

	# 将合并后的内容写入输出文件
	output_file_path = os.path.join(folder_path, merge_html)
	write_file(output_file_path, merged_content)
	print(f"HTML文件成功合并为{merge_html}。")

if __name__ == "__main__":
	if len(sys.argv) != 5:
		print("Usage: python merge_html.py -f <folder_path> -n <merge.html>")
		print("-f 指定html文件夹的路径, -n 指定html合并后的名字")
		print("example: python merge_html.py -f /Users/chentuo/Personal/myself/微信数据库/wechat_dump/result/人类 -n 人类.html")

	else:
		folder_path = sys.argv[2]
		merge_html = sys.argv[4]
		merge_html_files(folder_path, merge_html)
