import urllib.request
import urllib.error
import json
import concurrent.futures


class TimeoutException(Exception):
    """Exception raised when an operation times out."""
    pass


class Get_from_VolcEngine:
    """
    火山引擎大模型调用封装。

    采用同事版本的结构与调试输出，但默认 endpoint_id 使用当前项目的配置：
    ep-20260316000236-ck7h7
    """

    base_url = "https://ark.cn-beijing.volces.com/api/v3"

    def __init__(self, api_key: str = "", endpoint_id: str = ""):
        # 优先使用传入的 api_key，否则使用内置占位（需在环境中覆盖）
        if api_key == "":
            # 使用用户提供的豆包API Key（如需安全，请通过环境变量覆盖）
            self.api_key = "1b471ec6-3810-4300-b099-03aacf8f1de9"
        else:
            self.api_key = api_key

        # 默认使用当前项目正在使用的 endpoint_id
        if endpoint_id:
            self.endpoint_id = endpoint_id
        else:
            self.endpoint_id = "ep-20260316000236-ck7h7"

    def get_api_key(self) -> str:
        return self.api_key

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key

    def get_endpoint_id(self) -> str:
        return self.endpoint_id

    def set_endpoint_id(self, endpoint_id: str) -> None:
        self.endpoint_id = endpoint_id

    def get_msg(self, text: str) -> str:
        """
        调用火山引擎 Chat Completions 接口，返回模型回复文本。
        """

        def api_call() -> str:
            url = f"{self.base_url}/chat/completions"

            # 调试信息，便于排查线上问题
            print("VolcEngine API调用信息:")
            print(f"  URL: {url}")
            print(f"  Endpoint ID: {self.get_endpoint_id()}")
            print(f"  API Key: {self.get_api_key()[:10]}...")

            data = {
                "model": self.get_endpoint_id(),
                "messages": [
                    {"role": "user", "content": text},
                ],
            }

            json_data = json.dumps(data).encode("utf-8")
            print(f"  请求数据: {json_data[:200]}...")

            req = urllib.request.Request(
                url,
                data=json_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.get_api_key()}",
                },
                method="POST",
            )

            try:
                print("  发送请求...")
                with urllib.request.urlopen(req, timeout=180) as response:
                    response_text = response.read().decode("utf-8")
                    print(f"  响应状态: {response.status}")
                    print(f"  响应内容: {response_text[:200]}...")
                    result = json.loads(response_text)
                    return result["choices"][0]["message"]["content"]
            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8")
                print(f"VolcEngine API HTTP错误: {e.code}, 响应: {error_body}")
                raise Exception(f"VolcEngine API HTTP错误: {e.code}, 响应: {error_body}")
            except urllib.error.URLError as e:
                print(f"VolcEngine API URL错误: {e.reason}")
                raise Exception(f"VolcEngine API URL错误: {e.reason}")
            except Exception as e:
                print(f"VolcEngine API调用失败: {e}")
                raise e

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(api_call)
                try:
                    result = future.result(timeout=180)
                    return result
                except concurrent.futures.TimeoutError:
                    future.cancel()
                    raise TimeoutException("API call timed out after 180 seconds")
        except Exception as e:
            print(f"VolcEngine API调用失败: {e}")
            raise e
