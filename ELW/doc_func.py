import re
from . import func

def main_process(text):
    question_data = []
    questions = extract_questions(text)
    for question in questions:
        main_question = parse_main_question(question)
        question_data.append(main_question)
        print(f'main_question: {main_question}')
    return question_data

# 分割各道大题
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
    # print('result: ', result)
    print(f'extract_questions: {result}')
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
        'image': [], # 大题题干图片
        'sub_questions': [],
    }

    # 匹配问题类型 (如 'choice')
    question_type = re.match(r'^(.*?):', text)
    if question_type:
        main_question['question_type'] = question_type.group(1).strip()
        text = text.replace(question_type.group(0), '')  # 移除 question_type 部分

    # 提取大题题干
    qt_match = re.search(r'\(([1-4])\)', text)  # 寻找第一个 '(1)'格式
    if qt_match:
        # 如果找到 '(1)' 格式，提取到该格式文本之前
        question_text = text[:qt_match.start()].strip()
        text = text.replace(text[:qt_match.start()].strip(), '')  # 移除 question_text 部分

    # 提取 score
    score_pattern = r'\$(\d+(?:\.\d+)?)\$'
    score_match = re.search(score_pattern, question_text)
    if score_match:
        main_question['score'] = float(score_match.group(1))
        question_text = question_text.replace(score_match.group(0), '')  # 移除 score 部分
    # 提取 min 和 max
    range_pattern = r'\[(\d+)-(\d+)\]'
    range_match = re.search(range_pattern, question_text)
    if range_match:
        main_question['min'] = int(range_match.group(1))
        main_question['max'] = int(range_match.group(2))
        question_text = question_text.replace(range_match.group(0), '')  # 移除 range 部分
    # 提取 start 和 end
    time_range_pattern = r'\[([^\[\]-]+:[^\[\]-]+:[^\[\]-]+)-([^\[\]-]+:[^\[\]-]+:[^\[\]-]+)\]'
    time_range_match = re.search(time_range_pattern, question_text)
    if time_range_match:
        main_question['start'] = time_range_match.group(1)
        main_question['end'] = time_range_match.group(2)
        question_text = question_text.replace(time_range_match.group(0), '')  # 移除 time range 部分
    # 提取 images
    image_pattern = r'\(%(.*?)%\)'
    image_matches = re.findall(image_pattern, question_text)
    if image_matches:
        main_question['image']= image_matches
        question_text = re.sub(image_pattern, '', question_text).strip()  # 移除 image 部分
    main_question['question_text'] = question_text

    print('text: ', text)
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
    questions = []  # 小题题目文本分割结果列表
    # 逐一分割小题题目
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
        elif main_question['question_type'] == 'blank':
            print('blank_question: ', question)
            main_question['sub_questions'].append(func.extract_subtext_and_answers(question))

