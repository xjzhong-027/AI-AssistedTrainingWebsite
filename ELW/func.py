import re

# 处理大题
def extract_main_question(text):
    # 初始化返回字典
    result = {
        'question_text': '',
        'max': '',
        'min': '',
        'start': '',
        'end': ''
    }
    text = text.replace('\n', '').replace('\r', '').replace('\t', '')
    # 使用正则表达式提取 max, min, start, end 的值
    max_match = re.search(r'\[max:\s*(\d+)]', text)
    min_match = re.search(r'\[min:\s*(\d+)]', text)
    start_match = re.search(r'\[start:\s*([0-9]{2}:[0-9]{2}:[0-9]{2})]', text)
    end_match = re.search(r'\[end:\s*([0-9]{2}:[0-9]{2}:[0-9]{2})]', text)
    # 获取 question_text，去除参数部分
    question_text = re.split(r'\[.*?]', text, maxsplit=1)[0].strip()
    # 更新字典
    result['question_text'] = question_text
    result['max'] = int(max_match.group(1)) if max_match else ''
    result['min'] = int(min_match.group(1)) if min_match else ''
    result['start'] = start_match.group(1) if start_match else ''
    result['end'] = end_match.group(1) if end_match else ''
    print('main_question result: ', result)
    return result


# 处理选择题（单选+多选）
# 按题号分割题目，返回包含各个题目的列表，题号格式为(1)
def extract_choice_questions(text):
    # 使用正则表达式匹配题号，支持中文括号和英文括号，题号格式为(1)
    question_pattern = r'[\(\（]\d+[\)\）]'
    # 找到所有匹配的题号位置
    question_indices = [m.start() for m in re.finditer(question_pattern, text)]
    # 确保有题号
    if not question_indices:
        return []
    # 结果列表
    questions = []
    # 逐一分割题目
    for i in range(len(question_indices)):
        start_index = question_indices[i]
        # 如果是最后一个题目，取到文本结束
        end_index = question_indices[i + 1] if i + 1 < len(question_indices) else len(text)
        # 获取题目的文本
        question_text = text[start_index:end_index].strip()
        # 移除题号
        question_text = re.sub(r'^[\(\（]\d+[\)\）]', '', question_text).strip()
        questions.append(question_text)
    return questions

# 提取各个问题的信息
def process_choice_question(question):
    # 移除转义序列 \r\n\t
    question = question.replace('\n', '').replace('\r', '').replace('\t', '')
    # 默认值
    question_data = {
        'question_text': '',
        'score': 1.0,
        'label_count': 0,
        'A': '',
        'B': '',
        'C': '',
        'D': '',
        'answer': [],
        'tips': '',
        'analysis': ''
    }
    # 1. 优先匹配 '$数字$' 格式符号
    score_match = re.search(r'\$(\d+)\$', question)
    if score_match:
        # 如果找到 '$数字$'，则提取题干到该符号之前
        question_data['question_text'] = question[:score_match.start()].strip()
        question_data['score'] = float(score_match.group(1))
    else:
        # 2. 如果没有 '$数字$' 格式符号，检查是否存在 '[$A]' 格式
        option_match = re.search(r'\[\$([A])\]', question)  # 寻找 '[$A]', '[$B]' 等格式
        if option_match:
            # 如果找到 '[$A]' 格式，提取到该选项之前
            question_data['question_text'] = question[:option_match.start()].strip()
        else:
            # 如果没有 '[$A]' 格式，寻找 '[A]' 格式
            option_match = re.search(r'\[([A-D])\]', question)  # 寻找 '[A]', '[B]' 等格式
            if option_match:
                # 提取到第一个 '[A]' 格式选项之前
                question_data['question_text'] = question[:option_match.start()].strip()

    # 提取选项
    options = re.findall(r'([A-D])\]([^\[\n]+)', question)
    for label, option in options:
        question_data[label] = option.strip()
        question_data['label_count'] += 1

    # 提取答案 (假设答案是以[$X]格式给出的)
    answer_match = re.findall(r'\[\$(\w+)\]', question)
    question_data['answer'] = answer_match

    # 提取tips
    tips_match = re.search(r'\[tips:([^\]]+)\]', question)
    if tips_match:
        question_data['tips'] = tips_match.group(1).strip()

    # 提取analysis
    analysis_match = re.search(r'\[analysis:([^\]]+)\]', question)
    if analysis_match:
        question_data['analysis'] = analysis_match.group(1).strip()
    print(f'question_data: {question_data}')
    return question_data




# 处理改错题
def parse_text_modifications(input_text):
    # 正则匹配 [text:type:answer]
    pattern = r'\[([^:]*):([^:]*):([^]]+)\]'
    matches = re.finditer(pattern, input_text)
    print('matches: ', matches)
    # 初始化结果变量
    sub_list = []  # 小题题干
    text_list = []  # 需要改错的原小题文本
    type_list = []  # 改错类型
    answer_list = []  # 答案
    index_list = []  # 修订部分在原文本中的单词索引，以空格为分隔符
    last_end = 0  # 分割点初始化
    word_index = 0  # 当前单词索引

    # 遍历匹配
    for match in matches:
        text, op_type, answer = match.groups()
        start, end = match.span()
        # before_text = input_text[last_end:start]
        # sub_list.append(before_text)
        # 处理 type, answer 和 index
        text_list.append(text.strip())
        type_list.append(op_type.strip())
        answer_list.append(answer.strip())
        last_end = end  # 更新 last_end

    # 提取原文本中修订文本的前缀和后缀
    def extract_prefix_suffix(input_string):
        pattern = re.compile(r'(.*?)\[(.*?)\](.*)')
        match = pattern.match(input_string)
        if match:
            prefix = match.group(1).strip()
            suffix = match.group(3).strip()
        else:
            prefix = ''
            suffix = ''
        return prefix, suffix

    split_texts = input_text.split()
    print('split_texts: ', split_texts)
    before_text = ''
    index = 0
    ignore_count = 0  # 当修改类型为insert时，修订部分在原文本中的单词索引为插入位置的前一个单词的索引，因此在原文中不占据索引位置
    match_count = 0
    insert_pattern = r'.*:insert:.*'  # 判断修订类型为insert的题目
    for i, split_text in enumerate(split_texts):
        print(f"{i}: {split_text}")
        if re.search(pattern, split_text):
            match_count += 1
            prefix = extract_prefix_suffix(split_text)[0]
            suffix = extract_prefix_suffix(split_text)[1]
            if re.search(insert_pattern, split_text):
                print('find insert')
                ignore_count += 1
                index_list.append(index - 1)
                before_text = before_text + prefix + suffix + ' '
                sub_list.append(before_text)
                before_text = ''
                index = 0
            else:
                before_text = before_text + prefix + text_list[match_count - 1] + suffix + ' '
                print('test: ', text_list[match_count - 1])
                index_list.append(index)
                print('match example: ', split_texts[index + ignore_count])
                sub_list.append(before_text)
                before_text = ''
                index = 0
        else:
            before_text = before_text + split_text + ' '
            index += 1
    # 处理最后一段普通文本
    if last_end < len(input_text):
        sub_list[-1] = sub_list[-1] + input_text[last_end:]
        # sub_list.append(input_text[last_end:])
    # 返回结果
    return {
        'sub_list': sub_list,
        'text_list': text_list,
        'type_list': type_list,
        'answer_list': answer_list,
        'index_list': index_list
        # 'split_texts': split_texts,
    }

'''
# # 处理改错题
# def parse_text_modifications(input_text):
#     # 正则匹配 [text:type:answer]
#     pattern = r'\[([^:]*):([^:]*):([^]]+)\]'
#     matches = re.finditer(pattern, input_text)
#     print('matches: ', matches)
#     # 初始化结果变量
#     sub_list = []  # 小题题干
#     text_list = []  # 需要改错的原小题文本
#     type_list = []  # 改错类型
#     answer_list = []  # 答案
#     index_list = []  # 修订部分在原文本中的单词索引，以空格为分隔符
#     last_end = 0  # 分割点初始化
#     word_index = 0  # 当前单词索引
# 
#     # 遍历匹配
#     for match in matches:
#         text, op_type, answer = match.groups()
#         start, end = match.span()
#         # before_text = input_text[last_end:start]
#         # sub_list.append(before_text)
#         # 处理 type, answer 和 index
#         text_list.append(text.strip())
#         type_list.append(op_type.strip())
#         answer_list.append(answer.strip())
#         last_end = end  # 更新 last_end
# 
#     # 提取原文本中修订文本的前缀和后缀
#     def extract_prefix_suffix(input_string):
#         pattern = re.compile(r'(.*?)\[(.*?)\](.*)')
#         match = pattern.match(input_string)
#         if match:
#             prefix = match.group(1).strip()
#             suffix = match.group(3).strip()
#         else:
#             prefix = ''
#             suffix = ''
#         return prefix, suffix
# 
#     split_texts = input_text.split()
#     print('split_texts: ', split_texts)
#     before_text = ''
#     index = 0
#     ignore_count = 0  # 当修改类型为insert时，修订部分在原文本中的单词索引为插入位置的前一个单词的索引，因此在原文中不占据索引位置
#     match_count = 0
#     insert_pattern = r'.*:insert:.*'  # 判断修订类型为insert的题目
#     for i, split_text in enumerate(split_texts):
#         print(f"{i}: {split_text}")
#         if re.search(pattern, split_text):
#             match_count += 1
#             prefix = extract_prefix_suffix(split_text)[0]
#             suffix = extract_prefix_suffix(split_text)[1]
#             if re.search(insert_pattern, split_text):
#                 print('find insert')
#                 ignore_count += 1
#                 index_list.append(index - ignore_count)
#                 before_text = before_text + prefix + suffix + ' '
#                 sub_list.append(before_text)
#                 before_text = ''
#                 index += 1
#             else:
#                 before_text = before_text + prefix + text_list[match_count - 1] + suffix + ' '
#                 print('test: ', text_list[match_count - 1])
#                 index_list.append(index - ignore_count)
#                 print('match example: ', split_texts[index + ignore_count])
#                 sub_list.append(before_text)
#                 before_text = ''
#                 index += 1
#         else:
#             before_text = before_text + split_text + ' '
#             index += 1
#     # 处理最后一段普通文本
#     if last_end < len(input_text):
#         sub_list[-1] = sub_list[-1] + input_text[last_end:]
#         # sub_list.append(input_text[last_end:])
#     # 返回结果
#     return {
#         'sub_list': sub_list,
#         'text_list': text_list,
#         'type_list': type_list,
#         'answer_list': answer_list,
#         'index_list': index_list
#         # 'split_texts': split_texts,
#     }
'''




# 处理连线题
def extract_matching_questions(text):
    # 正则表达式匹配题号部分（支持中文和英文括号）,匹配的内容是：(1) 或 （1） 这种格式的题号
    pattern = r'([（(]\d+[）)])'
    # 按题号进行分割
    question_parts = re.split(pattern, text)
    print('question_parts: ', question_parts)
    # 移除空字符串，并将每个题目重新组合成题号 + 题目内容
    questions = []
    for i in range(1, len(question_parts), 2):
        # question_number = question_parts[i].strip()
        # print(f'question_number{i}: {question_number}')
        question_text = question_parts[i + 1].strip()
        print(f'question_text{i}: {question_text}')
        # 合并题号和题目内容
        # full_question = f"{question_number}{question_text}"
        # print(f'full_question{i}: {full_question}')
        questions.append(question_text)
    return questions

# 提取各个问题的信息
def process_matching_question(question_text):
    # 移除转义序列 \r\n\t
    question_text = question_text.replace('\r\n', '').replace('\n', '').replace('\r', '').replace('\t', '')
    print('question_text: ', question_text)
    result = {
        'question_text': '',
        'score': '',
        'option_label': '',
        'option_content': '',
        'tips': '',
        'analysis': ''
    }
    # 判断题目中是否包含 $数字$ 格式的分数
    score_match = re.search(r'\$(\d+(\.\d+)?)\$', question_text)
    if score_match:
        # 如果包含 $数字$ 格式，则提取 $数字$ 前的部分作为题干
        question_text_match = re.match(r'([^\$]+)', question_text)
        if question_text_match:
            result['question_text'] = question_text_match.group(1).strip()
        result['score'] = score_match.group(1)
    else:
        # 如果不包含 $数字$ 格式，则提取到第一个选项[A]或[B]等选项之前的部分作为题干
        question_text_match = re.match(r'([^\[]+)', question_text)
        if question_text_match:
            result['question_text'] = question_text_match.group(1).strip()
        result['score'] = '1.0'  # 如果没有指明分值，则返回默认分值1.0
    # 提取选项标签和选项内容 (格式: [A] A website)
    option_match = re.search(r'\[([A-Z])\](.*?)\s*(?=\[|$)', question_text)
    if option_match:
        result['option_label'] = option_match.group(1)
        result['option_content'] = option_match.group(2).strip()
    # 提取提示 (格式: [tips: some tips])
    tips_match = re.search(r'\[tips:([^\[]+)\]', question_text)
    if tips_match:
        result['tips'] = tips_match.group(1).strip()
    else:
        result['tips'] = ''  # 若没有提示，返回空值
    # 提取分析 (格式: [analysis: something])
    analysis_match = re.search(r'\[analysis:([^\[]+)\]', question_text)
    if analysis_match:
        result['analysis'] = analysis_match.group(1).strip()
    else:
        result['analysis'] = ''  # 若没有分析，返回空值
    return result













# 处理简答题
# 按题号分割题目，返回包含各个题目的列表，题号格式为(1)
def extract_comprehension_questions(text):
    # 使用正则表达式匹配题号，支持中文括号和英文括号，题号格式为(1)
    question_pattern = r'[\(\（]\d+[\)\）]'
    # 找到所有匹配的题号位置
    question_indices = [m.start() for m in re.finditer(question_pattern, text)]
    # 确保有题号
    if not question_indices:
        return []
    # 结果列表
    questions = []
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
    return questions


# 对各个题目的内容进行信息提取
def process_comprehension_question(question):
    result = {
        'question_text': "",
        'score': 1.0,  # 默认分数为 1.0
        'answer': "",
        'tips': "",
        'analysis': "",
    }
    # 首先使用正则表达式提取题干部分，优先匹配分值格式，即含有 $数字$ 格式的情况
    # 查找包含 $数字$ 的位置
    match_score = re.search(r'\$(\d+)\$', question)
    if match_score:
        # 如果找到$数字$，提取$数字$之前的部分作为题干
        result['question_text'] = re.split(r'\$\d+\$', question)[0].strip()
        result['score'] = float(match_score.group(1))  # 提取分数
    else:
        # 如果没有$数字$，则提取第一个[answer: 任意字符]之前的内容
        match_answer = re.search(r'\[answer:([^\]]+)\]', question)
        if match_answer:
            result['question_text'] = question.split('[answer:')[0].strip()
    # 提取答案部分
    match_answer = re.search(r'\[answer:([^\]]+)\]', question)
    if match_answer:
        result['answer'] = match_answer.group(1).strip()
    # 提取提示和分析部分
    match_tips = re.search(r'\[tips:([^\]]+)\]', question)
    if match_tips:
        result['tips'] = match_tips.group(1).strip()
    match_analysis = re.search(r'\[analysis:([^\]]+)\]', question)
    if match_analysis:
        result['analysis'] = match_analysis.group(1).strip()
    return result