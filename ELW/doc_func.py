import re
from . import func

def extract_questions(text):
    # 使用正则表达式匹配各个部分，注意匹配的是带有数字和括号的章节标题
    sections = re.split(r'(\([一二三四五六七八九十]+\))', text)

    # 清理分割结果，去除空字符串并合并标题和内容
    result = []
    for i in range(1, len(sections), 2):
        title = sections[i].strip()  # 章节标题
        content = sections[i + 1].strip() if i + 1 < len(sections) else ""
        print(title, content)
        # result.append(f"{title}{content}")
        result.append(content)
    print('result: ', result)
    return result

def parse_main_question(text):
    # 定义一个字典来存储所有提取的内容
    main_question = {
        'question_type': '',
        'question_text': '',
        'score': 1.0,
        'min': 1,
        'max': 3,
        'start': '',
        'end': '',
        'sub_questions': [],
    }

    # 匹配问题类型 (如 'choice')
    question_type = re.match(r'^(.*?):', text)
    if question_type:
        main_question['question_type'] = question_type.group(1).strip()
        text = text.replace(question_type.group(0), '')  # 移除 question_type 部分

    text_match = False
    # 提取 score
    score_pattern = r'\$(\d+(?:\.\d+)?)\$'
    score_match = re.search(score_pattern, text)
    if score_match:
        main_question['score'] = float(score_match.group(1))
        main_question['question_text'] = text.split(score_match.group(0))[0].strip()
        text_match = True
        text = text.replace(text.split(score_match.group(0))[0].strip(), '')  # 移除 question_text 部分
        text = text.replace(score_match.group(0), '')  # 移除 score 部分
    # 提取 min 和 max
    range_pattern = r'\[(\d+)-(\d+)\]'
    range_match = re.search(range_pattern, text)
    if range_match:
        main_question['min'] = int(range_match.group(1))
        main_question['max'] = int(range_match.group(2))
        if not text_match:
            main_question['question_text'] = text.split(range_match.group(0))[0].strip()
            text_match = True
            text = text.replace(text.split(range_match.group(0))[0].strip(), '')   # 移除 question_text 部分
        text = text.replace(range_match.group(0), '')  # 移除 range 部分
    # 提取 start 和 end
    time_range_pattern = r'\[([^\[\]-]+:[^\[\]-]+:[^\[\]-]+)-([^\[\]-]+:[^\[\]-]+:[^\[\]-]+)\]'
    time_range_match = re.search(time_range_pattern, text)
    if time_range_match:
        main_question['start'] = time_range_match.group(1)
        main_question['end'] = time_range_match.group(2)
        if not text_match:
            main_question['question_text'] = text.split(time_range_match.group(0))[0].strip()
            text_match = True
            text = text.replace(text.split(time_range_match.group(0))[0].strip(), '')   # 移除 question_text 部分
        text = text.replace(time_range_match.group(0), '')  # 移除 time range 部分
    if not text_match:
        qt_match = re.search(r'\(([1-4])\)', text)  # 寻找第一个 '(1)'格式
        if qt_match:
            # 如果找到 '(1)' 格式，提取到该格式文本之前
            main_question['question_text'] = text[:qt_match.start()].strip()
            text_match = True
            text = text.replace(text[:qt_match.start()].strip(), '') # 移除 question_text 部分
    parse_sub_question(text, main_question)

    return main_question

def parse_sub_question(text, main_question):
    # 使用正则表达式匹配题号，支持中文括号和英文括号，题号格式为(1)
    question_pattern = r'[\(\（]\d+[\)\）]'
    # 找到所有匹配的题号位置
    question_indices = [m.start() for m in re.finditer(question_pattern, text)]
    # 确保有题号
    if not question_indices:
        return []
    questions = []  # 结果列表
    # 逐一分割题目
    for i in range(len(question_indices)):
        start_index = question_indices[i]
        # 如果是最后一个题目，取到文本结束
        end_index = question_indices[i + 1] if i + 1 < len(question_indices) else len(text)
        # 获取题目的文本
        question_text = text[start_index:end_index].strip()
        # 移除题号
        question_text = re.sub(r'^[\(\（]\d+[\)\）]', '', question_text).strip()
        question_text = question_text.replace('\n', '').replace('\r', '').replace('\t', '')
        questions.append(question_text)
    for question in questions:
        if main_question['question_type'] == 'choice':
            main_question['sub_questions'].append(func.process_choice_question(question))
        elif main_question['question_type'] == 'correction':
            main_question['sub_questions'].append(func.parse_text_modifications(question))
        elif main_question['question_type'] == 'matching':
            main_question['sub_questions'].append(func.process_matching_question(question))
        elif main_question['question_type'] == 'comprehension':
            main_question['sub_questions'].append(func.process_comprehension_question(question))

