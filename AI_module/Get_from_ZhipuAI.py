from zhipuai import ZhipuAI
import concurrent.futures

class TimeoutException(Exception):
    """Exception raised when an operation times out."""
    pass

class Get_from_ZhipuAI:
    api_key=""

    def __init__(self, api_key=""):
        if api_key == "": self.api_key = "6e63ee57768871bcd6085697c95573fd.9YsvIoPbQD0jhcA7"
        else: self.api_key = api_key

    def get_api_key(self):
        return self.api_key

    def set_api_key(self, api_key):
        self.api_key = api_key

    def get_msg(self, text):
        def api_call():
            client = ZhipuAI(api_key=self.get_api_key())
            response = client.chat.completions.create(
                model="glm-4-flash",  # 请填写您要调用的模型名称
                messages=[
                    {"role": "user", "content": text},
                ],
            )
            return response.choices[0].message.content

        # 使用 ThreadPoolExecutor 来执行 API 调用，并设置超时时间
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(api_call)
            try:
                # 等待结果，最多等待 10 秒
                result = future.result(timeout=10)
                return result
            except concurrent.futures.TimeoutError:
                # 超时后取消任务
                future.cancel()
                raise TimeoutException("API call timed out after 10 seconds")