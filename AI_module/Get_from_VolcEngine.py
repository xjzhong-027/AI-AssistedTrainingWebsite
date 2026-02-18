import urllib.request
import urllib.error
import json
import concurrent.futures

class TimeoutException(Exception):
    """Exception raised when an operation times out."""
    pass

class Get_from_VolcEngine:
    api_key = ""
    base_url = "https://ark.cn-beijing.volces.com/api/v3"
    endpoint_id = "ep-20260219034644-f5qhx"

    def __init__(self, api_key="", endpoint_id=""):
        if api_key == "":
            # 使用用户提供的豆包API Key
            self.api_key = "1b471ec6-3810-4300-b099-03aacf8f1de9"
        else:
            self.api_key = api_key

        if endpoint_id:
            self.endpoint_id = endpoint_id

    def get_api_key(self):
        return self.api_key

    def set_api_key(self, api_key):
        self.api_key = api_key

    def get_endpoint_id(self):
        return self.endpoint_id

    def set_endpoint_id(self, endpoint_id):
        self.endpoint_id = endpoint_id

    def get_msg(self, text):
        def api_call():
            url = f"{self.base_url}/chat/completions"
            data = {
                "model": self.get_endpoint_id(),
                "messages": [
                    {"role": "user", "content": text},
                ],
            }

            json_data = json.dumps(data).encode('utf-8')

            req = urllib.request.Request(
                url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.get_api_key()}'
                },
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=180) as response:
                response_text = response.read().decode('utf-8')
                result = json.loads(response_text)
                return result["choices"][0]["message"]["content"]

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
