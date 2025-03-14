import re
from . import doc_func

def main_process(text):
    print('text_content: ', text)
    pages, page_list = paging_process(text)
    for i, page in enumerate(page_list):
        pages[i]['page_content'] = doc_func.main_process(page)
    print('pages: ', pages)


def paging_process(text):
    pattern = r'\[\%(.*?)\%\]'
    # 找到所有匹配的分隔符位置
    delimiter_indices = [m.span() for m in re.finditer(pattern, text)]
    if not delimiter_indices:
        return text
    time_list = []
    page_list = []
    prev_end = 0  # 上一个分隔符的结束位置
    # 遍历所有匹配的分隔符
    for start, end in delimiter_indices:
        page_list.append(text[prev_end:start].strip())
        time_list.append(text[start:end][2:-2])  # 去掉 [% 和 %]
        prev_end = end
    # 添加最后一个分隔符后的文本
    page_list.append(text[prev_end:].strip())
    page_list = [part for part in page_list if part]
    pages = []
    if len(page_list) == len(time_list):
        for i, page in enumerate(page_list):
            pages.append({
                'limited_time': time_list[i],
                'page_content': [],
            })
        print('paging_process: ', pages)
        return pages, page_list