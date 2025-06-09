#!/usr/bin/env python3
import sys
import re

def count_send_pfc(file_path):
    try:
        with open(file_path, 'r') as file:
            # 使用正则表达式匹配 "send pfc"（不区分大小写：re.IGNORECASE）
            pattern = re.compile(r"send pfc", re.IGNORECASE)
            count = 0
            for line in file:
                if pattern.search(line):
                    count += 1
            return count
    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 不存在！")
        sys.exit(1)

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("请输入文件路径：")

    count = count_send_pfc(file_path)
    print(f"send pfc 出现的次数: {count}")

if __name__ == "__main__":
    main()