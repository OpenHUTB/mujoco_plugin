import re
from datetime import datetime


# 列表项：缩进不超过 3 个空格的无序列表（-、*、+）或有序列表（数字加 .），且标记后紧跟内容
LIST_ITEM_RE = re.compile(r'^ {0,3}(?:[*+-]|(?P<number>\d+)\.)[ \t]+\S')
# 围栏代码块的开始或结束标记（``` 或 ~~~）
FENCE_RE = re.compile(r'^\s*(?P<fence>`{3,}|~{3,})')


def on_config(config, **kwargs):
    year = str(datetime.now().year)
    config.copyright = config.copyright.format(year=year)


def on_page_markdown(markdown, **kwargs):
    """在紧跟段落的列表前补一个空行，使 mkdocs 的渲染效果与 GitHub 一致。

    Python-Markdown 要求列表前必须有空行，否则列表项会被并入上一段落显示在同一行；
    而 GitHub（CommonMark）允许列表直接打断段落。这里按 CommonMark 的规则处理：
    无序列表和从 1 开始的有序列表可以打断段落。围栏代码块中的内容保持不变。
    """
    lines = markdown.split('\n')
    result = []
    fence = None  # 当前所在围栏代码块的开始标记
    in_list = False  # 是否处于列表块中（从列表项开始直到下一个空行）
    previous = ''

    for line in lines:
        fence_match = FENCE_RE.match(line)
        if fence is not None:
            # 结束标记需与开始标记字符相同、长度不小于开始标记，且后面没有其他内容
            if (fence_match
                    and fence_match.group('fence')[0] == fence[0]
                    and len(fence_match.group('fence')) >= len(fence)
                    and not line[fence_match.end():].strip()):
                fence = None
        elif fence_match:
            fence = fence_match.group('fence')
        elif not line.strip():
            in_list = False
        else:
            item_match = LIST_ITEM_RE.match(line)
            if item_match:
                number = item_match.group('number')
                if (not in_list
                        and _is_paragraph_line(previous)
                        and (number is None or int(number) == 1)):
                    result.append('')
                in_list = True

        result.append(line)
        previous = line

    return '\n'.join(result)


def _is_paragraph_line(line):
    """判断一行是否为普通段落文本（排除空行、缩进内容、HTML、表格和引用）。"""
    return bool(line.strip()) and not line.startswith((' ', '\t', '<', '|', '>'))
