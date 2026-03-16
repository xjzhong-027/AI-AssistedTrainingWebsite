import json
import re
import time
import threading
from typing import Optional, Dict, List, Any
from AI_module.Get_from_AI import Get_from_AI


class QuestionGenerationService:
    """AI自动出题服务"""
    
    ASSESSMENT_DIRECTIONS = {
        'main_idea': {
            'name': '主旨大意概括 (Main Idea / Gist)',
            'weight': 6,
            'example': '这段听力材料主要谈论了什么？或最适合本段材料的标题是什么？',
            'goal': '评估学生整合全部信息，把握内容核心与篇章主旨的综合概括能力。',
            'keywords': ['主要', '主旨', '标题', '概括', 'main idea', 'gist', 'title']
        },
        'cause_effect': {
            'name': '因果关系理解 (Cause and Effect)',
            'weight': 5,
            'example': '根据材料，某事件发生的主要原因是什么？或某个人物做出某个决定的直接后果是什么？',
            'goal': '评估学生理解信息之间逻辑关联的能力，而不仅仅是孤立的细节。',
            'keywords': ['原因', '结果', '导致', '因为', '所以', 'cause', 'effect', 'why', 'because']
        },
        'purpose_attitude': {
            'name': '目的与态度推断 (Purpose & Attitude)',
            'weight': 4,
            'example': '说话者讲述某个故事的主要目的是什么？或说话者对提及的某个现象持何种态度（支持、反对、担忧等）？',
            'goal': '评估学生超越字面意思，理解说话者意图、立场或情感倾向的推断能力。',
            'keywords': ['目的', '态度', '观点', '意图', 'purpose', 'attitude', 'opinion', 'intent']
        },
        'inference': {
            'name': '推理与结论 (Inference & Conclusion)',
            'weight': 3,
            'example': '根据材料内容，我们可以推断出什么？或对话最可能发生在什么场景（人物关系、场合）之下？',
            'goal': '评估学生的最高层次思维能力，要求其基于全文信息进行合理逻辑延伸，得出文中未明确陈述的结论。',
            'keywords': ['推 断', '结论', '推测', '暗示', 'infer', 'conclude', 'imply', 'suggest']
        },
        'vocabulary_context': {
            'name': '词汇在语境中的含义 (Vocabulary in Context)',
            'weight': 2,
            'example': '材料中出现的某个特定词语或短语（可能是习语、专业术语或多义词），在本文语境中实际指的是什么意思？',
            'goal': '评估学生结合上下文推测生词或熟词生义的能力，这是理解连贯语篇的关键。',
            'keywords': ['词汇', '含义', '意思', '短语', 'vocabulary', 'meaning', 'phrase', 'word']
        },
        'factual_detail': {
            'name': '事实细节捕捉 (Factual Detail)',
            'weight': 1,
            'example': '材料中明确提到了事件发生的时间、地点、人物、数字或具体名称是什么？',
            'goal': '评估学生获取和记忆直接信息的基本能力。这是听力理解的基石。',
            'keywords': ['时间', '地点', '人物', '数字', '名称', 'when', 'where', 'who', 'how many']
        }
    }
    
    DIFFICULTY_CONFIG = {
        'easy': {
            'description': '简单',
            'vocabulary_level': '基础词汇（初中水平），使用常见日常词汇',
            'sentence_complexity': '简单句为主，直接引用原文，不进行改写',
            'answer_location': '答案直接出现在原文中，无需推理，可直接定位',
            'distractor_design': '干扰项与正确答案差异明显，容易排除，使用原文未提及的常识性错误或明显错误的数字/时间',
            'reasoning_level': '零推理，直接在原文中找到答案',
            'question_stem': '题干直接使用原文中的关键词，不进行改写',
            'analysis_style': '直接指出答案在原文中的具体位置',
            'design_requirements': '''
【简单难度题目设计要求】
1. 题干设计：
   - 直接使用原文中的关键词和短语
   - 问题形式简单明了，如"What is...?", "When did...?", "How many...?"
   - 不进行同义替换或改写
2. 答案设计：
   - 答案在原文中可直接找到，原句原词
   - 不需要任何推理或理解
   - 信息明确、单一
3. 干扰项设计：
   - 与原文内容明显不符
   - 使用原文未提及的常识性错误
   - 数字/时间明显错误（如数量级差异）
   - 干扰项之间差异明显
4. 解析要求：
   - 直接引用原文句子
   - 指出答案所在位置（如"原文第X句提到..."）
'''
        },
        'medium': {
            'description': '中等',
            'vocabulary_level': '中等词汇（高中水平），可使用一些高级词汇但需上下文可理解',
            'sentence_complexity': '复合句，适度改写原文，使用同义替换',
            'answer_location': '答案需要简单推理，信息可能分散在1-2句中，需要理解后得出',
            'distractor_design': '干扰项有一定迷惑性，包含部分正确信息，存在偷换概念或因果倒置的情况',
            'reasoning_level': '简单推理，需要理解因果关系、对比关系或时间顺序',
            'question_stem': '题干可对原文进行适度改写，使用同义替换，但意思明确',
            'analysis_style': '需要解释推理过程，说明如何从原文得出答案',
            'design_requirements': '''
【中等难度题目设计要求】
1. 题干设计：
   - 可对原文进行适度改写
   - 使用同义词替换原文词汇
   - 问题形式可稍复杂，如"What can we learn about...?", "Why did...?"
2. 答案设计：
   - 需要理解原文后得出
   - 信息可能分散在相邻的1-2句中
   - 需要简单的因果推理或信息整合
3. 干扰项设计：
   - 包含原文部分信息但结论错误
   - 偷换概念或因果倒置
   - 使用原文词汇但搭配错误
   - 过度绝对化（如使用"always", "never"等）
4. 解析要求：
   - 解释推理过程
   - 说明原文信息与答案的关联
'''
        },
        'hard': {
            'description': '困难',
            'vocabulary_level': '高级词汇（大学/专业水平），可使用专业术语、习语、抽象词汇',
            'sentence_complexity': '复杂句，深度改写和概括，需要理解隐含含义',
            'answer_location': '答案需要深度推理，整合全文或多段信息，可能涉及隐含意思',
            'distractor_design': '干扰项迷惑性强，逻辑陷阱多，存在似是而非的选项，需要深度理解才能排除',
            'reasoning_level': '深度推理，需要综合分析、推断隐含信息、理解作者意图或态度',
            'question_stem': '题干高度概括或抽象化，需要理解深层含义，可能涉及推断、概括、评价',
            'analysis_style': '需要详细解释推理链条，说明如何综合多处信息得出结论',
            'design_requirements': '''
【困难难度题目设计要求】
1. 题干设计：
   - 高度概括或抽象化
   - 需要理解深层含义
   - 问题形式复杂，如"What can be inferred...?", "What is the author's attitude...?", "Which best describes...?"
2. 答案设计：
   - 需要综合多段信息推理得出
   - 可能涉及隐含意思、作者态度、言外之意
   - 需要深度理解和分析
3. 干扰项设计：
   - 逻辑看似合理但结论错误
   - 过度推断或以偏概全
   - 使用原文词汇制造"似是而非"的选项
   - 部分正确但不完整
   - 需要深度理解才能排除
4. 解析要求：
   - 详细解释推理链条
   - 说明如何综合多处信息
   - 分析干扰项的错误原因
'''
        }
    }
    
    QUESTION_TYPE_CONFIG = {
        'choice': {
            'name': '选择题',
            'description': '包含题干、选项和正确答案',
            'output_format': '''
[
  {
    "main_question": {
      "question_text": "大题题干（如：听录音选择正确答案）",
      "question_type": "choice"
    },
    "sub_questions": [
      {
        "question_text": "小题问题",
        "options": {
          "A": "选项A内容",
          "B": "选项B内容",
          "C": "选项C内容",
          "D": "选项D内容"
        },
        "correct_answer": "A",
        "analysis": "答案解析",
        "score": 2.0
      }
    ]
  }
]
'''
        },
        'matching': {
            'name': '连线题',
            'description': '包含左右两列匹配项',
            'output_format': '''
[
  {
    "main_question": {
      "question_text": "大题题干（如：将左右两列进行匹配）",
      "question_type": "matching"
    },
    "sub_questions": [
      {
        "question_text": "连线题说明",
        "left_items": {
          "1": "左侧项1",
          "2": "左侧项2"
        },
        "right_items": {
          "A": "右侧项A",
          "B": "右侧项B"
        },
        "correct_matching": {"1": "A", "2": "B"},
        "analysis": "答案解析",
        "score": 2.0
      }
    ]
  }
]
'''
        },
        'fill-blank': {
            'name': '填空题',
            'description': '根据听力内容填写空白处',
            'output_format': '''
[
  {
    "main_question": {
      "question_text": "大题题干（如：根据听力内容填空）",
      "question_type": "text"
    },
    "sub_questions": [
      {
        "question_text": "填空题内容，用______表示空白处",
        "answer": "正确答案",
        "analysis": "答案解析",
        "score": 1.0
      }
    ]
  }
]
'''
        },
        'fill-blank-transcript': {
            'name': '填空题（听力原文考察）',
            'description': '基于听力原文进行挖空考察',
            'output_format': '''
[
  {
    "main_question": {
      "question_text": "根据听力原文填空",
      "question_type": "text"
    },
    "sub_questions": [
      {
        "question_text": "听力原文内容，其中考察词汇用______代替",
        "answer": "被挖空的单词",
        "analysis": "该词在原文中的含义和用法",
        "score": 1.0
      }
    ]
  }
]
'''
        },
        'fill-blank-summary': {
            'name': '填空题（主旨大意考察）',
            'description': '基于主旨大意进行挖空考察',
            'output_format': '''
[
  {
    "main_question": {
      "question_text": "阅读以下文章主旨大意，填写空白处",
      "question_type": "text"
    },
    "sub_questions": [
      {
        "question_text": "主旨大意文章内容，关键部分用______代替",
        "answer": "被挖空的关键词",
        "analysis": "该关键词在文章中的作用",
        "score": 1.0
      }
    ]
  }
]
'''
        },
        'comprehension': {
            'name': '主观题',
            'description': '开放式问答，需要学生作答',
            'output_format': '''
[
  {
    "main_question": {
      "question_text": "大题题干（如：根据听力内容回答问题）",
      "question_type": "comprehension"
    },
    "sub_questions": [
      {
        "question_text": "问题内容",
        "answer": "参考答案",
        "analysis": "答案解析",
        "score": 5.0
      }
    ]
  }
]
'''
        }
    }
    
    FEW_SHOT_EXAMPLES = {
        'choice': '''
【示例】
听力原文：The weather today is sunny and warm. The temperature is about 25 degrees Celsius. It's a perfect day for outdoor activities like hiking and picnicking.

【正确输出】
[
  {
    "main_question": {
      "question_text": "听录音，选择正确答案",
      "question_type": "choice"
    },
    "sub_questions": [
      {
        "question_text": "What is the weather like today?",
        "options": {
          "A": "Rainy and cold",
          "B": "Sunny and warm",
          "C": "Cloudy and cool",
          "D": "Windy and hot"
        },
        "correct_answer": "B",
        "analysis": "原文明确提到 'The weather today is sunny and warm'，因此正确答案是B。",
        "score": 2.0
      },
      {
        "question_text": "What is the temperature today?",
        "options": {
          "A": "15 degrees Celsius",
          "B": "20 degrees Celsius",
          "C": "25 degrees Celsius",
          "D": "30 degrees Celsius"
        },
        "correct_answer": "C",
        "analysis": "原文提到 'The temperature is about 25 degrees Celsius'，因此正确答案是C。",
        "score": 2.0
      }
    ]
  }
]
''',
        'comprehension': '''
【示例】
听力原文：The library opens at 9 AM and closes at 9 PM on weekdays. On weekends, it opens at 10 AM and closes at 6 PM. Students can borrow up to 5 books at a time.

【正确输出】
[
  {
    "main_question": {
      "question_text": "根据听力内容回答问题",
      "question_type": "comprehension"
    },
    "sub_questions": [
      {
        "question_text": "What are the opening hours of the library on weekdays?",
        "answer": "The library opens at 9 AM and closes at 9 PM on weekdays.",
        "analysis": "这是一个细节信息题，答案直接来自原文。",
        "score": 3.0
      },
      {
        "question_text": "How many books can students borrow at a time?",
        "answer": "Students can borrow up to 5 books at a time.",
        "analysis": "原文最后一句明确说明了借书数量限制。",
        "score": 2.0
      }
    ]
  }
]
''',
        'fill-blank-transcript': '''
【示例】
听力原文：The weather today is sunny and warm. The temperature is about 25 degrees Celsius. It's a perfect day for outdoor activities like hiking and picnicking.

【正确输出】
[
  {
    "main_question": {
      "question_text": "根据听力原文填空，每空一词。",
      "question_type": "text"
    },
    "sub_questions": [
      {
        "question_text": "The weather today is ______ and warm. The temperature is about 25 degrees Celsius.",
        "answer": "sunny",
        "analysis": "原文第一句明确提到 'The weather today is sunny and warm'，sunny意为晴朗的。",
        "score": 1.0
      },
      {
        "question_text": "It's a perfect day for ______ activities like hiking and picnicking.",
        "answer": "outdoor",
        "analysis": "原文提到 'outdoor activities'，outdoor意为户外的，与hiking和picnicking等活动相呼应。",
        "score": 1.0
      }
    ]
  }
]
''',
        'fill-blank-summary': '''
【示例】
听力原文：The library opens at 9 AM and closes at 9 PM on weekdays. On weekends, it opens at 10 AM and closes at 6 PM. Students can borrow up to 5 books at a time. The library also provides study rooms and computer facilities for students.

【正确输出】
[
  {
    "main_question": {
      "question_text": "阅读以下关于图书馆的介绍，填写空白处。",
      "question_type": "text"
    },
    "sub_questions": [
      {
        "question_text": "The library has different opening hours on weekdays and ______. On weekdays, it opens earlier at 9 AM and closes later at 9 PM. Students can borrow a maximum of ______ books at one time. Besides books, the library also offers study rooms and ______ facilities for student use.",
        "answer": "weekends|5|computer",
        "analysis": "文章总结了图书馆的开放时间、借书限制和设施。第一空填weekends（周末），第二空填5（数量），第三空填computer（电脑设施）。",
        "score": 2.0
      }
    ]
  }
]
'''
    }

    _task_storage: Dict[int, Dict] = {}
    _task_counter = 0
    _lock = threading.Lock()
    
    def __init__(self, model='VolcEngine'):
        self.ai_client = Get_from_AI(model=model)
        self.conversation_history: List[Dict[str, str]] = []
    
    @classmethod
    def create_task(cls) -> int:
        """创建新任务并返回任务ID"""
        with cls._lock:
            cls._task_counter += 1
            task_id = cls._task_counter
            cls._task_storage[task_id] = {
                'status': 'pending',
                'message': '任务已创建',
                'questions': [],
                'created_at': time.time()
            }
            return task_id
    
    @classmethod
    def get_task_status(cls, task_id: int) -> Optional[Dict]:
        """获取任务状态"""
        return cls._task_storage.get(task_id)
    
    @classmethod
    def update_task(cls, task_id: int, **kwargs):
        """更新任务状态"""
        if task_id in cls._task_storage:
            cls._task_storage[task_id].update(kwargs)
    
    def generate_questions_async(
        self,
        task_id: int,
        transcript: str,
        question_type: str,
        difficulty: str,
        count: int,
        focus_points: List[str],
        additional_requirements: str
    ):
        """异步生成题目（在线程中执行）"""
        try:
            self.update_task(task_id, status='processing', message='正在分析听力原文...')
            
            result = self._generate_with_retry(
                transcript=transcript,
                question_type=question_type,
                difficulty=difficulty,
                count=count,
                focus_points=focus_points,
                additional_requirements=additional_requirements,
                max_retries=3
            )
            
            if result['success']:
                self.conversation_history = [
                    {"role": "system", "content": f"你是一位专业的英语听力出题专家。以下是需要基于的听力原文：\n\n{transcript}"},
                    {"role": "user", "content": "请根据要求生成题目"},
                    {"role": "assistant", "content": json.dumps(result['questions'], ensure_ascii=False)}
                ]
                
                self.update_task(
                    task_id,
                    status='completed',
                    message='题目生成完成',
                    questions=result['questions'],
                    conversation_history=self.conversation_history
                )
            else:
                self.update_task(
                    task_id,
                    status='failed',
                    message=result.get('message', '生成失败'),
                    suggestions=result.get('suggestions', [])
                )
        except Exception as e:
            self.update_task(
                task_id,
                status='failed',
                message=f'生成过程出错: {str(e)}'
            )
    
    def _generate_with_retry(
        self,
        transcript: str,
        question_type: str,
        difficulty: str,
        count: int,
        focus_points: List[str],
        additional_requirements: str,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """带重试机制的题目生成"""
        
        for attempt in range(max_retries):
            try:
                prompt = self._build_generation_prompt(
                    transcript=transcript,
                    question_type=question_type,
                    difficulty=difficulty,
                    count=count,
                    focus_points=focus_points,
                    additional_requirements=additional_requirements,
                    attempt=attempt + 1
                )
                
                response = self.ai_client.get_answer(prompt)
                
                if not response or response.startswith("未接收到"):
                    continue
                
                result = self._parse_generation_response(response, question_type)
                
                if result['success'] and len(result['questions']) > 0:
                    return result
                
                if attempt < max_retries - 1:
                    repair_result = self._attempt_repair(
                        response=response,
                        error=result.get('message', ''),
                        question_type=question_type,
                        transcript=transcript,
                        count=count
                    )
                    if repair_result['success']:
                        return repair_result
                        
            except Exception as e:
                print(f"第{attempt + 1}次尝试失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
        
        return self._get_detailed_error_result(transcript, question_type, count)
    
    def _build_generation_prompt(
        self,
        transcript: str,
        question_type: str,
        difficulty: str,
        count: int,
        focus_points: List[str],
        additional_requirements: str,
        attempt: int = 1
    ) -> str:
        """构建题目生成提示"""
        
        type_config = self.QUESTION_TYPE_CONFIG.get(question_type, self.QUESTION_TYPE_CONFIG['choice'])
        few_shot = self.FEW_SHOT_EXAMPLES.get(question_type, self.FEW_SHOT_EXAMPLES['choice'])
        
        difficulty_config = self.DIFFICULTY_CONFIG.get(difficulty, self.DIFFICULTY_CONFIG['medium'])
        
        assessment_distribution = self._calculate_assessment_distribution(count, focus_points)
        assessment_instructions = self._build_assessment_instructions(assessment_distribution, count)
        
        focus_text = ""
        if focus_points:
            focus_names = [self.ASSESSMENT_DIRECTIONS.get(fp, {}).get('name', fp) for fp in focus_points]
            focus_text = f"\n- 指定考察重点：{', '.join(focus_names)}"
        
        additional_text = ""
        if additional_requirements:
            additional_text = f"\n- 其他要求：{additional_requirements}"
        
        retry_hint = ""
        if attempt > 1:
            retry_hint = f"\n\n【重要】这是第{attempt}次尝试，请务必严格按照JSON格式输出，确保格式正确！"
        
        special_instructions = ""
        if question_type == 'fill-blank-transcript':
            special_instructions = """
【填空题（听力原文考察）特殊要求】
1. 直接使用听力原文的内容作为题目文本
2. 选择有考察价值的单词进行挖空，包括：
   - 重要词汇（如动词、形容词、名词）
   - 关键信息词（如数字、时间、地点）
   - 易混淆词汇
3. 用______（6个下划线）表示空白处
4. 每个空白处只挖一个单词
5. 确保挖空后句子语法正确，上下文通顺
6. 答案必须是原文中出现的准确单词
"""
        elif question_type == 'fill-blank-summary':
            special_instructions = """
【填空题（主旨大意考察）特殊要求】
1. 首先根据听力原文生成200字以上的文章主旨大意摘要
2. 摘要应该：
   - 概括文章的主要内容和观点
   - 语言简洁、逻辑清晰
   - 保留关键信息和重要细节
3. 在摘要中对关键部分进行挖空，包括：
   - 核心概念词
   - 重要细节信息
   - 逻辑连接词
4. 用______（6个下划线）表示空白处
5. 每个空白处可以是一个单词或短语
6. 如果一题有多个空，答案用|分隔，如：answer1|answer2|answer3
"""
        
        prompt = f"""你是一位专业的英语听力出题专家。请仔细阅读以下内容并生成高质量的题目。

【重要规则】
1. 你必须严格按照JSON数组格式输出，不要添加任何解释性文字
2. 题目必须完全基于提供的听力原文，不能编造内容
3. 如果原文信息不足以生成指定数量的题目，请生成尽可能多的题目
4. 每道题目必须有明确的答案和解析
5. 不要使用```json```等markdown标记，直接输出JSON数组
{special_instructions}
【考察方向分配要求】
{assessment_instructions}

【顺序原则 - 必须严格遵守】
1. 题序与信息序严格对应：
   - 第一题的答案信息必须来自材料最开头部分（如第一段或对话的开场）
   - 第二题的答案信息必须紧接着第一题答案信息之后出现
   - 以此类推，倒数第二题的答案信息来自材料靠后部分
2. 禁止信息回溯或跳跃：
   - 后一题的答案出处，不能在听力时间线上早于前一题的答案出处
   - 确保学生能像"跟随导航"一样，按材料播放的先后顺序找到每道题的答案
3. 主旨大意题位置要求：
   - 主旨大意概括类题目必须放在最后一题
   - 此类题目考察学生对整个素材的整体理解，答案可来自全文任何部分
   - 其他所有题目严格按材料顺序排列

【Few-shot示例】
{few_shot}

【听力原文】
{transcript}

【出题要求】
- 题目类型：{type_config['name']} - {type_config['description']}
- 题目数量：{count}道小题
- 难度等级：{difficulty_config['description']}{focus_text}{additional_text}

【难度详细要求】
{difficulty_config['design_requirements']}

【输出格式】
请输出一个JSON数组，每个元素包含main_question和sub_questions：
{type_config['output_format']}

【输出检查清单】
□ JSON格式正确，可以被解析
□ 每道题都有question_text
□ 选择题有options和correct_answer
□ 主观题/填空题有answer字段作为参考答案
□ 每道题都有analysis解析
□ 分数设置合理
□ 题目覆盖了多种考察方向，不只是细节题
□ 严格遵循顺序原则（主旨大意题除外）
□ 题目难度符合{difficulty_config['description']}等级的要求{retry_hint}

现在请直接输出JSON数组，不要有任何其他内容："""

        return prompt
    
    def _calculate_assessment_distribution(self, total_count: int, focus_points: List[str]) -> Dict[str, int]:
        """根据权重计算每个考察方向的题目数量"""
        distribution = {}
        
        if focus_points:
            for key in focus_points:
                if key in self.ASSESSMENT_DIRECTIONS:
                    distribution[key] = distribution.get(key, 0) + 1
        
        if not distribution:
            total_weight = sum(d['weight'] for d in self.ASSESSMENT_DIRECTIONS.values())
            remaining = total_count
            
            sorted_directions = sorted(
                self.ASSESSMENT_DIRECTIONS.items(),
                key=lambda x: x[1]['weight'],
                reverse=True
            )
            
            for key, direction in sorted_directions:
                if remaining <= 0:
                    break
                
                weight = direction['weight']
                proportion = weight / total_weight
                allocated = max(1, round(total_count * proportion))
                
                if allocated > remaining:
                    allocated = remaining
                
                if remaining > 0:
                    distribution[key] = allocated
                    remaining -= allocated
            
            if remaining > 0:
                for key in distribution:
                    if remaining <= 0:
                        break
                    distribution[key] += 1
                    remaining -= 1
        
        total_allocated = sum(distribution.values())
        if total_allocated != total_count:
            diff = total_count - total_allocated
            if diff > 0:
                distribution['factual_detail'] = distribution.get('factual_detail', 0) + diff
            elif diff < 0:
                for key in list(distribution.keys()):
                    if distribution[key] > 1 and diff < 0:
                        distribution[key] -= 1
                        diff += 1
        
        return distribution
    
    def _build_assessment_instructions(self, distribution: Dict[str, int], total_count: int) -> str:
        """构建考察方向分配说明"""
        instructions = []
        instructions.append(f"本次需要生成{total_count}道题目，请按以下考察方向分配：\n")
        
        for key, count in distribution.items():
            if count > 0:
                direction = self.ASSESSMENT_DIRECTIONS[key]
                instructions.append(f"【{direction['name']}】约{count}道")
                instructions.append(f"  - 示例：{direction['example']}")
                instructions.append(f"  - 目标：{direction['goal']}\n")
        
        instructions.append("\n【分配原则】")
        instructions.append("- 权重高的考察方向优先分配题目")
        instructions.append("- 如果原文内容适合某类考察，可适当调整数量")
        instructions.append("- 确保题目覆盖多种考察方向，避免全部是细节题")
        instructions.append("- 每道题的analysis中请说明该题考察的是哪个方向")
        
        return '\n'.join(instructions)
    
    def _parse_generation_response(self, response: str, question_type: str) -> Dict[str, Any]:
        """解析AI生成的题目响应"""
        result = self._extract_json_from_response(response)
        
        if result is not None:
            questions = []
            
            if isinstance(result, list):
                questions = result
            elif isinstance(result, dict):
                if 'questions' in result:
                    questions = result['questions']
                elif 'main_question' in result:
                    questions = [result]
                else:
                    questions = [result]
            
            validated_questions = []
            for q in questions:
                validated_q = self._validate_question(q, question_type)
                if validated_q:
                    validated_questions.append(validated_q)
            
            if validated_questions:
                return {
                    'success': True,
                    'questions': validated_questions,
                    'raw_response': response[:500] if response else ''
                }
        
        return {
            'success': False,
            'message': '无法解析AI响应，JSON格式可能不正确',
            'questions': [],
            'raw_response': response[:500] if response else ''
        }
    
    def _validate_question(self, question: Dict, question_type: str) -> Optional[Dict]:
        """验证并规范化题目数据"""
        if not isinstance(question, dict):
            return None
        
        validated = {
            'main_question': {},
            'sub_questions': []
        }
        
        if 'main_question' in question:
            validated['main_question'] = {
                'question_text': question['main_question'].get('question_text', ''),
                'question_type': question['main_question'].get('question_type', question_type)
            }
        else:
            validated['main_question'] = {
                'question_text': question.get('question_text', ''),
                'question_type': question.get('question_type', question_type)
            }
        
        if validated['main_question']['question_type'] == 'fill-blank':
            validated['main_question']['question_type'] = 'text'
        
        if 'sub_questions' in question:
            sub_qs = question['sub_questions']
        else:
            sub_qs = [question]
        
        for sq in sub_qs:
            if not isinstance(sq, dict):
                continue
                
            validated_sq = {
                'question_text': sq.get('question_text', ''),
                'score': float(sq.get('score', 2.0)),
                'analysis': sq.get('analysis', '')
            }
            
            if 'options' in sq and isinstance(sq['options'], dict):
                validated_sq['options'] = sq['options']
                validated_sq['correct_answer'] = sq.get('correct_answer', 'A')
            elif 'answer' in sq:
                validated_sq['answer'] = sq['answer']
            elif 'reference_answer' in sq:
                validated_sq['answer'] = sq['reference_answer']
            
            if 'left_items' in sq:
                validated_sq['left_items'] = sq['left_items']
                validated_sq['right_items'] = sq.get('right_items', {})
                validated_sq['correct_matching'] = sq.get('correct_matching', {})
            
            validated['sub_questions'].append(validated_sq)
        
        if not validated['sub_questions']:
            return None
            
        return validated
    
    def _extract_json_from_response(self, response: str) -> Optional[Any]:
        """从AI响应中提取JSON"""
        if not response:
            return None
        
        text = response.strip()
        
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        json_match = re.search(r'\[[\s\S]*\]', text)
        if json_match:
            try:
                cleaned = self._clean_json_string(json_match.group())
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass
        
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                cleaned = self._clean_json_string(json_match.group())
                return json.loads(cleaned)
            except json.JSONDecodeError:
                pass
        
        try:
            cleaned = self._clean_json_string(text)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None
    
    def _clean_json_string(self, text: str) -> str:
        """清理JSON字符串中的控制字符"""
        cleaned = ''
        in_string = False
        escape_next = False
        
        for i, char in enumerate(text):
            if escape_next:
                cleaned += char
                escape_next = False
                continue
            
            if char == '\\':
                cleaned += char
                escape_next = True
                continue
            
            if char == '"' and (i == 0 or text[i-1] != '\\'):
                in_string = not in_string
                cleaned += char
                continue
            
            if in_string:
                if ord(char) < 32 and char not in ['\n', '\r', '\t']:
                    continue
                elif char == '\n':
                    cleaned += '\\n'
                elif char == '\r':
                    cleaned += '\\r'
                elif char == '\t':
                    cleaned += '\\t'
                else:
                    cleaned += char
            else:
                if ord(char) >= 32 or char in [' ', '\n', '\r', '\t']:
                    cleaned += char
        
        return cleaned
    
    def _attempt_repair(
        self,
        response: str,
        error: str,
        question_type: str,
        transcript: str,
        count: int
    ) -> Dict[str, Any]:
        """尝试修复失败的响应"""
        
        repair_prompt = f"""之前的生成出现了问题，请重新生成正确的JSON格式题目。

【错误信息】
{error}

【原始响应（前1000字符）】
{response[:1000]}

【听力原文】
{transcript[:2000]}

【要求】
1. 严格按照JSON数组格式输出
2. 生成{count}道{self.QUESTION_TYPE_CONFIG.get(question_type, {}).get('name', '题目')}
3. 不要添加任何解释性文字
4. 不要使用markdown标记

请直接输出JSON数组："""

        try:
            repaired_response = self.ai_client.get_answer(repair_prompt)
            return self._parse_generation_response(repaired_response, question_type)
        except Exception:
            return {'success': False, 'message': '修复失败'}
    
    def _get_detailed_error_result(
        self,
        transcript: str,
        question_type: str,
        count: int
    ) -> Dict[str, Any]:
        """生成详细的错误信息和用户建议"""
        
        error_msg = "AI生成题目时遇到问题。"
        suggestions = []
        
        if not transcript or len(transcript.strip()) < 50:
            error_msg += "听力原文内容过短，可能无法生成足够的题目。"
            suggestions.append("请确保素材有足够的听力原文内容")
        elif len(transcript) > 10000:
            error_msg += "听力原文过长，建议分段处理。"
            suggestions.append("尝试减少题目数量")
        else:
            error_msg += "请尝试以下方法："
            suggestions.extend([
                "调整题目类型或难度后重试",
                "减少题目数量",
                "提供更具体的出题要求",
                "检查听力原文是否有效"
            ])
        
        return {
            'success': False,
            'message': error_msg,
            'questions': [],
            'suggestions': suggestions
        }
    
    def chat_revise(
        self,
        message: str,
        transcript: str,
        current_questions: List[Dict],
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """多轮对话修订题目"""
        
        if not conversation_history:
            conversation_history = [
                {"role": "system", "content": f"你是一位专业的英语听力出题专家。以下是需要基于的听力原文：\n\n{transcript}"}
            ]
        
        intent = self._recognize_intent(message)
        
        user_message = message
        if current_questions:
            user_message = f"{message}\n\n当前题目状态：\n{json.dumps(current_questions, ensure_ascii=False, indent=2)}"
        
        conversation_history.append({"role": "user", "content": user_message})
        
        prompt = self._build_chat_prompt(conversation_history, intent)
        
        try:
            response = self.ai_client.get_answer(prompt)
            conversation_history.append({"role": "assistant", "content": response})
            
            result = self._parse_generation_response(response, 'auto')
            
            if result['success']:
                result['conversation_history'] = conversation_history
                return result
            else:
                return {
                    'success': False,
                    'message': '无法解析修订结果，请尝试更明确的指令',
                    'questions': current_questions,
                    'conversation_history': conversation_history,
                    'suggestions': self._get_intent_suggestions(intent)
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'修订失败: {str(e)}',
                'questions': current_questions,
                'conversation_history': conversation_history
            }
    
    def _recognize_intent(self, message: str) -> str:
        """识别用户意图"""
        message_lower = message.lower()
        
        if any(kw in message_lower for kw in ['难', '简单', '难度', '更难', '更简单']):
            return 'modify_difficulty'
        elif any(kw in message_lower for kw in ['类型', '改成', '换成', '选择题', '填空题', '主观题']):
            return 'change_type'
        elif any(kw in message_lower for kw in ['增加', '添加', '再来', '更多', '加一道']):
            return 'add_questions'
        elif any(kw in message_lower for kw in ['错误', '修改', '改正', '不对', '改一下']):
            return 'fix_errors'
        elif any(kw in message_lower for kw in ['删除', '去掉', '移除']):
            return 'remove_question'
        else:
            return 'general'
    
    def _build_chat_prompt(self, conversation_history: List[Dict], intent: str) -> str:
        """构建多轮对话提示"""
        messages = []
        for msg in conversation_history:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                messages.append(f"[系统指令]\n{content}")
            elif role == 'user':
                messages.append(f"[教师]\n{content}")
            elif role == 'assistant':
                messages.append(f"[AI助手]\n{content[:500]}...")
        
        intent_hint = {
            'modify_difficulty': '请根据教师要求调整题目难度，修改题目内容使其更难或更简单。',
            'change_type': '请根据教师要求更改题目类型，保持题目内容的核心考察点。',
            'add_questions': '请根据教师要求增加新的题目，确保新题目与现有题目不重复。',
            'fix_errors': '请根据教师指出的问题修改题目内容。',
            'remove_question': '请根据教师要求删除指定题目。',
            'general': '请根据教师的具体要求修改题目。'
        }.get(intent, '请根据教师的具体要求修改题目。')
        
        return "\n\n".join(messages) + f"\n\n【处理要求】\n{intent_hint}\n\n请输出修订后的完整题目JSON数组，不要添加任何解释性文字："
    
    def _get_intent_suggestions(self, intent: str) -> List[str]:
        """根据意图返回建议"""
        suggestions = {
            'modify_difficulty': [
                "请明确指定难度等级：简单、中等、困难",
                "例如：把所有题目改成困难难度"
            ],
            'change_type': [
                "请明确指定目标题目类型",
                "例如：把第一题改成填空题"
            ],
            'add_questions': [
                "请指定要添加的题目数量",
                "例如：再添加2道选择题"
            ],
            'fix_errors': [
                "请指出具体需要修改的内容",
                "例如：第一题的答案应该是B"
            ],
            'remove_question': [
                "请指定要删除的题目编号",
                "例如：删除第二题"
            ]
        }
        return suggestions.get(intent, ['请更详细地描述您的需求'])

