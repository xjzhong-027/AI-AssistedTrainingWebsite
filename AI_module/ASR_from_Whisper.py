"""
使用 Whisper 将音频/视频文件转为文字（transcript）。
依赖：pip install openai-whisper，且需安装 FFmpeg 并加入 PATH。
"""
import os
import traceback


class ASR_from_Whisper:
    model = None
    model_name = "base"

    def __init__(self, model_name="base"):
        self.model_name = model_name

    def load_model(self):
        """加载 Whisper 模型"""
        try:
            import whisper
            if self.model is None:
                print(f"正在加载 Whisper 模型: {self.model_name}...")
                self.model = whisper.load_model(self.model_name)
                print("Whisper 模型加载成功！")
        except ImportError:
            raise ImportError("请先安装 openai-whisper: pip install openai-whisper")
        except Exception as e:
            raise Exception(f"加载 Whisper 模型失败: {str(e)}")

    def transcribe_audio(self, audio_file_path, language="en"):
        """
        使用 Whisper 将音频/视频文件转换为文字

        Args:
            audio_file_path: 音频/视频文件路径
            language: 语言代码（默认 'en' 为英语）

        Returns:
            识别出的文字内容
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"文件不存在: {audio_file_path}")

        try:
            self.load_model()
            print(f"开始语音识别: {audio_file_path}")
            try:
                result = self.model.transcribe(
                    audio_file_path,
                    language=language,
                    word_timestamps=False,
                    fp16=False
                )
            except Exception as e:
                print(f"Whisper 内置方法失败: {str(e)}")
                try:
                    import subprocess
                    subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                except FileNotFoundError:
                    raise RuntimeError(
                        "未找到 FFmpeg！请先安装 FFmpeg。\n"
                        "Windows: 下载 https://github.com/BtbN/FFmpeg-Builds/releases 解压并将 bin 加入 PATH\n"
                        "或: conda install ffmpeg"
                    )
                raise e
            transcript = result["text"].strip()
            print(f"语音识别完成，识别长度: {len(transcript)} 字符")
            return transcript
        except RuntimeError:
            raise
        except Exception as e:
            error_msg = f"语音识别失败: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            if "ffmpeg" in str(e).lower() or "file not found" in str(e).lower():
                raise RuntimeError(
                    "语音识别失败：未找到 FFmpeg！请安装 FFmpeg 并加入 PATH 后重试。"
                )
            raise Exception(error_msg)
