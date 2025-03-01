import re

# 处理大题
def extract_main_question(text):
    # 定义正则表达式模式
    score_pattern = r'\$(\d+(?:\.\d+)?)\$'
    range_pattern = r'\[(\d+)-(\d+)\]'
    # time_range_pattern = r'\[(\d{2}:\d{2}:\d{2})-(\d{2}:\d{2}:\d{2})\]'
    time_range_pattern = r'\[([^-]+)-([^\]]+)\]'
    # 初始化结果字典
    result = {
        'question_text': '',
        'min': 1,
        'max': 3,
        'start': '',
        'end': '',
        'score': 1.0
    }
    text_match = False
    # 提取 score
    score_match = re.search(score_pattern, text)
    if score_match:
        result['score'] = float(score_match.group(1))
        result['question_text'] = text.split(score_match.group(0))[0].strip()
        text_match = True
        text = text.replace(score_match.group(0), '')  # 移除 score 部分
    # 提取 min 和 max
    range_match = re.search(range_pattern, text)
    if range_match:
        result['min'] = int(range_match.group(1))
        result['max'] = int(range_match.group(2))
        result['question_text'] = text.split(range_match.group(0))[0].strip()
        text_match = True
        text = text.replace(range_match.group(0), '')  # 移除 range 部分
    # 提取 start 和 end
    time_range_match = re.search(time_range_pattern, text)
    if time_range_match:
        result['start'] = time_range_match.group(1)
        result['end'] = time_range_match.group(2)
        result['question_text'] = text.split(time_range_match.group(0))[0].strip()
        text_match = True
        text = text.replace(time_range_match.group(0), '')  # 移除 time range 部分
    # 提取 question_text
    if not text_match:
        result['question_text'] = text.strip()
    return result

    '''
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
    '''

# 处理选择题（单选+多选）
# 按题号分割题目，返回包含各个题目的列表，题号格式为(1)
def extract_choice_questions(text):
    text = text.replace('\n', '').replace('\r', '').replace('\t', '')
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
    question_data = {
        'question_text': '',
        'label_count': 0,
        'A': '',
        'B': '',
        'C': '',
        'D': '',
        'answer': [],
        'tips': '',
        'analysis': ''
    }
    # 提取tips
    tips_match = re.search( r'-\*([^*]+)\*-', question)
    if tips_match:
        question_data['tips'] = tips_match.group(1).strip()
        question = question.replace(tips_match.group(0), '')  # 移除 tips 部分

    # 提取analysis
    analysis_match = re.search(r'-\*\*([^*]+)\*\*-', question)
    if analysis_match:
        question_data['analysis'] = analysis_match.group(1).strip()
        question = question.replace(analysis_match.group(0), '') # 移除 analysis 部分

    # 检查是否存在 '[$A]' 格式
    option_match = re.search(r'\[\$([A])\]', question)  # 寻找 '[$A]'格式
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


    print(f'question_data: {question_data}')
    return question_data
    '''
    # 移除转义序列 \r\n\t
    # question = question.replace('\n', '').replace('\r', '').replace('\t', '')
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
    '''



# 处理改错题
def parse_text_modifications(input_text):
    # 正则匹配 [text:type:answer]
    pattern = r'\[([^:]*):([^:]*):([^]]+)\]'
    matches = re.finditer(pattern, input_text)
    # print('matches: ', matches)
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
        # print(f"{i}: {split_text}")
        if re.search(pattern, split_text):
            match_count += 1
            prefix = extract_prefix_suffix(split_text)[0]
            suffix = extract_prefix_suffix(split_text)[1]
            if re.search(insert_pattern, split_text):
                # print('find insert')
                ignore_count += 1
                index_list.append(index - 1)
                before_text = before_text + prefix + suffix + ' '
                sub_list.append(before_text)
                before_text = ''
                index = 0
            else:
                before_text = before_text + prefix + text_list[match_count - 1] + suffix + ' '
                # print('test: ', text_list[match_count - 1])
                index_list.append(index)
                # print('match example: ', split_texts[index + ignore_count])
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
    text = text.replace('\r\n', '').replace('\n', '').replace('\r', '').replace('\t', '')
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
        # print(f'question_text{i}: {question_text}')
        # 合并题号和题目内容
        # full_question = f"{question_number}{question_text}"
        # print(f'full_question{i}: {full_question}')
        questions.append(question_text)
    return questions

# 提取各个问题的信息
def process_matching_question(question_text):
    # question_text = question_text.replace('\r\n', '').replace('\n', '').replace('\r', '').replace('\t', '')
    print('question_text: ', question_text)
    result = {
        'question_text': '',
        'option_label': '',
        'option_content': '',
        'tips': '',
        'analysis': ''
    }
    # 提取tips
    tips_match = re.search(r'-\*([^*]+)\*-', question_text)
    if tips_match:
        result['tips'] = tips_match.group(1).strip()
        question_text = question_text.replace(tips_match.group(0), '')  # 移除 tips 部分
    # 提取analysis
    analysis_match = re.search(r'-\*\*([^*]+)\*\*-', question_text)
    if analysis_match:
        result['analysis'] = analysis_match.group(1).strip()
        question_text = question_text.replace(analysis_match.group(0), '')  # 移除 analysis 部分

    # 提取到第一个选项[A]或[B]等选项之前的部分作为题干
    question_text_match = re.match(r'([^\[]+)', question_text)
    if question_text_match:
        result['question_text'] = question_text_match.group(1).strip()
    # 提取选项标签和选项内容 (格式: [A] A website)
    option_match = re.search(r'\[([A-Z])\](.*?)\s*(?=\[|$)', question_text)
    if option_match:
        result['option_label'] = option_match.group(1)
        result['option_content'] = option_match.group(2).strip()
    return result

'''
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
    '''



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
    return questions

# 对各个题目的内容进行信息提取
def process_comprehension_question(question):
    result = {
        'question_text': "",
        'answer': "",
        'tips': "",
        'analysis': "",
    }
    # 提取tips
    tips_match = re.search(r'-\*([^*]+)\*-', question)
    if tips_match:
        result['tips'] = tips_match.group(1).strip()
        question = question.replace(tips_match.group(0), '')  # 移除 tips 部分
    # 提取analysis
    analysis_match = re.search(r'-\*\*([^*]+)\*\*-', question)
    if analysis_match:
        result['analysis'] = analysis_match.group(1).strip()
        question = question.replace(analysis_match.group(0), '')  # 移除 analysis 部分
    # 提取答案部分
    match_answer = re.search(r'\[\$([^\]]+)\]', question)
    if match_answer:
        result['answer'] = match_answer.group(1).strip()
        result['question_text'] = question.split('[$')[0].strip() #提取第一个[answer: 任意字符]之前的内容作为题干
    return result


# 处理填空题
def extract_blank_questions(text):
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
    return questions

# 对填空题小题各个题目信息进行提取
def extract_subtext_and_answers(question):
    # 使用正则表达式匹配 [1] 之前的内容和剩余内容
    pattern = r'^(.*?)(\[1\].*)$'
    match = re.match(pattern, question, re.DOTALL)
    if match:
        sub_texts = match.group(1).strip()  # 提取 [1] 之前的内容
        print('blank_subtexts: ', sub_texts)
        sub_answers = match.group(2).strip()  # 提取剩余内容
        print('blank_subanswers: ', sub_answers)
    else:
        sub_texts = question  # 如果没有匹配到，整个文本作为 sub_texts
        sub_answers = ""  # sub_answers 为空
    # result = {
    #     'sub_texts': sub_texts,
    #     'sub_answers': sub_answers
    # }
    # print('result: ', result)


    # 提取sub_questions和sub_index
    def extract_sub_questions(sub_text):
        pattern = r'__\d+__'
        split_texts = sub_texts.split()
        print('split_texts: ', split_texts)
        last_index = 0
        index = -1
        sub_question = ''
        sub_questions = []
        index_list = []
        for i, split_text in enumerate(split_texts):
            if re.search(pattern, split_text):
                sub_questions.append(sub_question)
                index_list.append(index)
                sub_question = ''
                index = -1
                last_index = i
            else:
                index += 1
                sub_question = sub_question + split_text + ' '
        if last_index < len(split_texts):
            for i in range(last_index + 1, len(split_texts)):
                sub_questions[-1] = sub_questions[-1] + ' ' + split_texts[i]
        result = {
            'sub_questions': sub_questions,
            'index_list': index_list,
        }
        # print('result2: ', result)
        return result

    sub_results = extract_sub_questions(sub_texts)
    sub_questions = sub_results['sub_questions']
    index_list = sub_results['index_list']
    # print('sub_answers: ', sub_answers)
    question_datas = [{'question_text': sub_questions[i],
                      'index': index_list[i],
                      'answer_list': [],
                      'tips': '',
                      'analysis': ''}
                     for i in range(len(sub_questions))]
    # print('question_datas: ', question_datas)

    # 提取sub_texts中的信息
    def extract_sub_answers(sub_answers):
        # 使用正则表达式匹配
        pattern = r'\[\d+\]'
        parts = re.split(pattern, sub_answers)
        # 去掉第一个空字符串（如果存在）
        if parts[0].strip() == '':
            parts = parts[1:]
        answer_texts = [part.strip() for part in parts]
        # print('answer_texts: ', answer_texts)
        return answer_texts
    answer_texts = extract_sub_answers(sub_answers)
    for i, answer_text in enumerate(answer_texts):
        # print('answer_text: ', answer_text)
        # 提取tips
        tips_match = re.search(r'-\*([^*]+)\*-', answer_text)
        if tips_match:
            question_datas[i]['tips'] = tips_match.group(1).strip()
            answer_text = answer_text.replace(tips_match.group(0), '')  # 移除 tips 部分
        # 提取analysis
        analysis_match = re.search(r'-\*\*([^*]+)\*\*-', answer_text)
        if analysis_match:
            question_datas[i]['analysis'] = analysis_match.group(1).strip()
            answer_text = answer_text.replace(analysis_match.group(0), '')  # 移除 analysis 部分

        answers = answer_text.strip().split(';')
        for answer in answers:
            if answer:
                question_datas[i]['answer_list'].append(answer)
    # print('question_datas: ', question_datas)
    return question_datas

