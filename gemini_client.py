import google.generativeai as genai
from config import Config
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        """初始化 Gemini 客户端"""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY 未设置，请在 .env 文件中配置")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
    def generate_answer(self, question: str) -> str:
        """
        根据面试问题生成回答
        
        Args:
            question (str): 面试官的问题
            
        Returns:
            str: AI 生成的回答建议
        """
        try:
            # 构建完整的提示词
            full_prompt = f"{Config.SYSTEM_PROMPT}\n\n面试官问题：{question}\n\n请提供回答建议："
            
            # 调用 Gemini API
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                logger.info(f"成功生成回答，问题：{question[:50]}...")
                return response.text.strip()
            else:
                logger.warning("Gemini API 返回空响应")
                return "抱歉，我暂时无法为这个问题提供回答建议。"
                
        except Exception as e:
            logger.error(f"调用 Gemini API 失败：{str(e)}")
            return f"生成回答时出现错误：{str(e)}"
    
    def test_connection(self) -> bool:
        """
        测试 Gemini API 连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            response = self.model.generate_content("Hello")
            return bool(response.text)
        except Exception as e:
            logger.error(f"Gemini API 连接测试失败：{str(e)}")
            return False
