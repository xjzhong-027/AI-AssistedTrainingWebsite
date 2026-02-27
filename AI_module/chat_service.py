"""
AI 聊天服务（火山引擎）

提供用户消息 → AI 回复的对话能力，供前端 AIWindow 等组件调用。
"""
import os
from typing import Optional
from datetime import datetime

from .Get_from_VolcEngine import Get_from_VolcEngine


# 环境变量配置（与项目现有 VolcEngine 配置一致）
VOLCENGINE_API_KEY = os.getenv('VOLCENGINE_API_KEY', os.getenv('USER_AI_API_KEY', ''))
VOLCENGINE_ENDPOINT_ID = os.getenv('VOLCENGINE_ENDPOINT_ID', 'ep-20260219034644-f5qhx')


class ChatService:
    """AI 聊天服务，使用火山引擎生成回复"""

    def __init__(self, api_key: Optional[str] = None, endpoint_id: Optional[str] = None):
        key = api_key or VOLCENGINE_API_KEY or ''
        ep = endpoint_id or VOLCENGINE_ENDPOINT_ID or ''
        self._client = Get_from_VolcEngine(api_key=key, endpoint_id=ep)

    def get_reply(self, message: str, context: Optional[dict] = None) -> str:
        """
        发送用户消息，获取 AI 回复

        Args:
            message: 用户消息内容
            context: 可选上下文（practice_id, page_id, sub_question_id 等）

        Returns:
            AI 回复文本
        """
        message = (message or '').strip()
        if not message:
            raise ValueError('消息内容不能为空')

        # 若有上下文，可拼接到 prompt 中增强效果（当前简单直接转发）
        prompt = message
        if context:
            ctx_parts = []
            if context.get('practice_id'):
                ctx_parts.append(f'[练习ID: {context["practice_id"]}]')
            if context.get('page_id'):
                ctx_parts.append(f'[页面ID: {context["page_id"]}]')
            if context.get('sub_question_id'):
                ctx_parts.append(f'[题目ID: {context["sub_question_id"]}]')
            if ctx_parts:
                prompt = f"{' '.join(ctx_parts)}\n\n{message}"

        return self._client.get_msg(prompt)
