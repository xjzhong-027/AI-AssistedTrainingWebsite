from AI_module.AI_module_local import AI_module_local
from .Get_from_ZhipuAI import Get_from_ZhipuAI
from .Get_from_VolcEngine import Get_from_VolcEngine
import copy


class Get_from_AI:
    __prompt_variables = {"题型": "", "题目数量": 0, "难度": "", "格式要求": "", "材料": "", "重点考察内容": "",
                          "其他要求": "", "原文":"", "题目":"", "参考答案":"", "学生回答":"", "其他要求_评分":"", "transcript":""}
    __prompt_template = {"题目生成": "请你为英语听力网站生成题目，要求：\
                            \n1.依据给出的材料生成\
                            \n2.题型：{题型}\
                            \n3.题目数量：{题目数量}\
                            \n4.难度：{难度}\
                            \n4.格式要求：{格式要求}\
                            \n5.材料：{材料}\
                            \n6.重点考察内容：{重点考察内容}\
                            \n7.其他要求：{其他要求}\
                            ",
                "题目评分": "原文：{原文}\
                           \n题目：{题目}\
                           \n学生回答：'{学生回答}'\
                           \n评分标准：1. 基本与参考答案无关的或没有作答的为0分 2.完全匹配参考答案关键词的100分 3.部分匹配参考答案内关键词的，每个关键词得到30分，最多不超过100分 4. 此外每有一个语法错误扣5分 5.最低得分为0分\
                           \n其他要求：{其他要求_评分}\
                           \n请你根据参考答案为学生回答打出评分:\
                           \n参考答案：'{参考答案}'",
                "素材分析": "请根据以下视频/音频的文本内容（transcript）进行分析，并以JSON格式返回结果：\
                            \n\nTranscript内容：\n{transcript}\n\n请返回以下JSON格式的内容，不要有其他额外文字：\
                            \n{\"title\": \"简短的标题（不超过20个词）\", \"theme\": \"主题（1-2句话概括）\", \
                            \"abstract\": \"摘要（3-5句话概括主要内容）\", \"keywords\": \"关键词（用逗号分隔的3-5个关键词）\"}",
                         }

    AI_model_name = ""
    local = AI_module_local()
    m = None

    def __init__(self, model="VolcEngine"):
        self.prompt = ""
        self.AI_model_name = model   #默认使用火山引擎（豆包）
        if model == "Local":
            try:
                pass
                # self.m = AI_module_local()
                # self.m = qwen_m()
            except:
                pass
        elif model == "ZhipuAI":
            self.m = Get_from_ZhipuAI()
        elif model == "VolcEngine":
            self.m = Get_from_VolcEngine()

    def get_prompt_template(self, key):
        return copy.deepcopy(self.__prompt_template[key])

    # my_prompt可以处理字符串或dict类型的输入进行修改。
    def set_prompt_template(self, my_prompt, my_key=None):
        if isinstance(my_prompt, dict):
            for k, v in my_prompt.items():
                self.__prompt_template[k] = v
        elif not my_key:
            self.__prompt_template = my_prompt
            return "您最好知道自己在干什么"
        elif isinstance(my_prompt, str):
            self.__prompt_template[my_key] = my_prompt

        return copy.deepcopy(self.__prompt_template)

    def get_prompt(self, my_key=None):
        if my_key == "题目评分": return self.__prompt_template["题目评分"].format(**self.__prompt_variables)
        elif my_key == "题目生成": return self.__prompt_template["题目生成"].format(**self.__prompt_variables)
        elif my_key == "素材分析": return self.__prompt_template["素材分析"].format(**self.__prompt_variables)

    def get_prompt_variables(self):
        return self.__prompt_variables

    def set_prompt_variables(self, my_dict=None, my_key=None, my_value=None, mode="update"):
        if mode == "update":
            if isinstance(my_dict, dict):
                self.__prompt_variables.update(my_dict)
            elif isinstance(my_key, str):
                self.__prompt_variables[my_key] = my_value
        elif mode == "remove":
            if isinstance(my_key, str): self.__prompt_variables.pop(my_key)
        elif mode == "cover":
            if isinstance(my_dict, dict): self.__prompt_variables = my_dict
        else:
            raise TypeError("Wrong input or mode.")

        return copy.deepcopy(self.__prompt_variables)

    def get_AI_module_name(self):
        return self.AI_model_name

    def set_AI_module_name(self, module):
        self.AI_model_name = module

    def get_answer(self, text=""):
        model = self.get_AI_module_name()

        if text == "": return "未接收到输入文本。"
        elif model == "VolcEngine":
            try:
                res = self.m.get_msg(text)
                return res
            except Exception as e:
                print(f"VolcEngine API调用失败: {e}")
                return self.local.get_answer_once(text)
        elif model == "ZhipuAI":
            try:
                res = self.m.get_msg(text)
                return res
            except Exception as e:
                print(e)
                return self.local.get_answer_once(text)
        elif model == "Local":
            return self.m.get_answer_once(text)