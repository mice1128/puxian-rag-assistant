"""
vLLM Service - 通过 OpenAI 兼容 API 调用 vLLM 推理引擎
"""
import requests
import json
from typing import List, Dict, Optional


class VLLMService:
    """vLLM API 服务客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8001/v1"):
        """
        初始化 vLLM 服务客户端
        
        Args:
            base_url: vLLM API 服务地址
        """
        self.base_url = base_url
        self.model_name = None
        self._check_service()
    
    def _check_service(self):
        """检查 vLLM 服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            if response.status_code == 200:
                models = response.json()
                if models.get("data"):
                    self.model_name = models["data"][0]["id"]
                    print(f"✓ vLLM 服务连接成功，使用模型: {self.model_name}")
                else:
                    print("⚠ vLLM 服务可访问，但未找到模型")
            else:
                print(f"⚠ vLLM 服务响应异常: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ 无法连接到 vLLM 服务 ({self.base_url}): {e}")
            print("  请确保 vLLM 服务器已启动！")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None
    ) -> str:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            top_p: Top-p 采样参数
            stop: 停止词列表
        
        Returns:
            生成的文本
        """
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
            }
            
            if stop:
                payload["stop"] = stop
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                error_msg = f"vLLM API 错误 ({response.status_code}): {response.text}"
                print(error_msg)
                return f"[生成失败: {error_msg}]"
        
        except requests.exceptions.Timeout:
            return "[生成超时]"
        except requests.exceptions.RequestException as e:
            return f"[请求失败: {e}]"
        except Exception as e:
            return f"[未知错误: {e}]"
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        多轮对话
        
        Args:
            messages: 对话历史，格式为 [{"role": "user/assistant", "content": "..."}]
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            top_p: Top-p 采样参数
        
        Returns:
            生成的回复
        """
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"[API 错误: {response.status_code}]"
        
        except Exception as e:
            return f"[生成失败: {e}]"


# 全局单例
_vllm_service = None


def get_vllm_service(base_url: str = "http://127.0.0.1:8001/v1") -> VLLMService:
    """获取 vLLM 服务单例"""
    global _vllm_service
    if _vllm_service is None:
        _vllm_service = VLLMService(base_url)
    return _vllm_service
