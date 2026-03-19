"""
Kimi (Moonshot) AI服务封装
提供与Moonshot API的交互功能，支持联网搜索、Token计算和文件分析
"""
import json
from typing import List, Dict, Any, AsyncGenerator, Optional
from openai import AsyncOpenAI
import httpx
from app.core.config import settings
from loguru import logger
import aiofiles
import os


class MoonshotService:
    """Kimi (Moonshot) AI服务类"""

    def __init__(self):
        self._client = None
        self._default_model = settings.MOONSHOT_MODEL
        self._api_key = settings.MOONSHOT_API_KEY
        self._base_url = settings.MOONSHOT_BASE_URL
        self._timeout = settings.MOONSHOT_TIMEOUT

    def get_model(self, user_model: Optional[str] = None) -> str:
        """
        获取要使用的模型

        Args:
            user_model: 用户指定的模型，如果为None则使用默认模型

        Returns:
            模型ID
        """
        if user_model:
            logger.info(f"使用用户指定模型: {user_model}")
            return user_model
        return self._default_model

    @property
    def client(self):
        """延迟初始化客户端，避免启动时阻塞"""
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=self._timeout
            )
            logger.info(f"Kimi (Moonshot)客户端初始化完成，默认模型: {self._default_model}")
        return self._client

    async def estimate_tokens(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None
    ) -> int:
        """
        估算Token数量
        
        使用Kimi官方API计算请求的token数
        
        Args:
            messages: 消息列表
            model: 模型名称，默认使用配置的模型
            
        Returns:
            int: 估算的token数量
        """
        try:
            # 构建请求数据
            request_data = {
                "model": model or self.model,
                "messages": messages
            }
            
            # 调用Kimi Token估算API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self._base_url}/tokenizers/estimate-token-count",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "data" in result and "total_tokens" in result["data"]:
                        total_tokens = result["data"]["total_tokens"]
                        logger.debug(f"Token估算完成: {total_tokens} tokens")
                        return total_tokens
                    else:
                        logger.warning(f"Token估算返回格式异常: {result}")
                        return 0
                else:
                    logger.error(f"Token估算API调用失败: {response.status_code} - {response.text}")
                    return 0
                    
        except Exception as e:
            logger.error(f"Token估算异常: {str(e)}")
            return 0

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """
        聊天补全
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
            
        Returns:
            聊天响应
        """
        try:
            use_model = self.get_model(model)
            
            params = {
                "model": use_model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            if stream:
                return await self.client.chat.completions.create(**params)
            else:
                response = await self.client.chat.completions.create(**params)
                return response
                
        except Exception as e:
            logger.error(f"聊天请求失败: {str(e)}")
            raise

    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            
        Yields:
            文本片段
        """
        try:
            use_model = self.get_model(model)
            
            params = {
                "model": use_model,
                "messages": messages,
                "temperature": temperature,
                "stream": True
            }
            
            if max_tokens:
                params["max_tokens"] = max_tokens
            
            stream_response = await self.client.chat.completions.create(**params)
            
            async for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"流式聊天失败: {str(e)}")
            raise

    async def web_search(
        self,
        query: str,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        联网搜索
        
        使用Kimi的联网搜索功能获取实时信息
        
        Args:
            query: 搜索查询
            model: 模型名称
            
        Returns:
            包含回答和引用信息的字典
        """
        try:
            use_model = self.get_model(model)
            
            messages = [
                {
                    "role": "system",
                    "content": "你是一个有帮助的AI助手。请使用联网搜索功能获取最新信息来回答用户问题。"
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
            
            # 使用支持联网的模型
            response = await self.client.chat.completions.create(
                model=use_model,
                messages=messages,
                temperature=0.7,
                tools=[{
                    "type": "web_search"
                }]
            )
            
            content = response.choices[0].message.content
            
            return {
                "answer": content,
                "query": query,
                "model": use_model
            }
            
        except Exception as e:
            logger.error(f"联网搜索失败: {str(e)}")
            raise

    async def upload_file(self, file_path: str, purpose: str = "file-extract") -> Dict[str, Any]:
        """
        上传文件到Kimi API
        
        Args:
            file_path: 本地文件路径
            purpose: 文件用途，默认为 "file-extract"（提取内容）
                    可选: "file-extract", "image", "video"
        
        Returns:
            文件信息，包含文件ID
        """
        try:
            url = f"{self._base_url}/files"
            headers = {
                "Authorization": f"Bearer {self._api_key}"
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                with open(file_path, 'rb') as f:
                    files = {'file': (os.path.basename(file_path), f)}
                    data = {'purpose': purpose}
                    
                    response = await client.post(
                        url,
                        headers=headers,
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"文件上传成功: {result.get('id')}")
                        return result
                    else:
                        logger.error(f"文件上传失败: {response.status_code} - {response.text}")
                        raise Exception(f"文件上传失败: {response.text}")
                        
        except Exception as e:
            logger.error(f"文件上传异常: {str(e)}")
            raise

    async def get_file_content(self, file_id: str) -> str:
        """
        获取已上传文件的内容（文本提取结果）
        
        Args:
            file_id: 文件ID
        
        Returns:
            文件内容文本
        """
        try:
            url = f"{self._base_url}/files/{file_id}/content"
            headers = {
                "Authorization": f"Bearer {self._api_key}"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    content = response.text
                    logger.info(f"文件内容获取成功: {file_id}")
                    return content
                else:
                    logger.error(f"文件内容获取失败: {response.status_code}")
                    raise Exception(f"文件内容获取失败: {response.text}")
                    
        except Exception as e:
            logger.error(f"文件内容获取异常: {str(e)}")
            raise

    async def analyze_medical_report(
        self,
        file_path: str,
        report_type: str = "general",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析医疗报告文件

        流程：
        1. 上传PDF文件到Kimi API (purpose="file-extract")
        2. 获取文件提取的文本内容
        3. 调用Kimi AI分析内容并返回JSON格式结果
        """
        try:
            # 1. 上传文件
            logger.info(f"开始上传医疗报告: {file_path}")
            file_info = await self.upload_file(file_path, purpose="file-extract")
            file_id = file_info.get('id')

            # 2. 获取文件内容
            logger.info(f"获取文件内容: {file_id}")
            file_content = await self.get_file_content(file_id)

            # 3. 构建分析提示词 - 强化 JSON 格式要求
            system_prompt = """你是一位资深体检医生和健康管理专家。请对上传的体检报告进行专业分析。

【重要】你必须直接返回纯 JSON 对象，不要添加任何 markdown 代码块标记（如 ```json），不要添加任何解释性文字。

严格按照以下 JSON 格式输出：
{
    "report_summary": {
        "report_type": "报告类型",
        "exam_date": "体检日期",
        "exam_center": "体检机构",
        "overall_assessment": "总体评估"
    },
    "indicators": [
        {
            "name": "指标名称",
            "value": "检测值",
            "unit": "单位",
            "reference_range": "参考范围",
            "status": "正常/异常/偏高/偏低",
            "interpretation": "临床意义解读"
        }
    ],
    "abnormal_findings": [
        {
            "item": "异常项目",
            "severity": "轻度/中度/重度",
            "description": "异常描述",
            "suggestion": "建议措施"
        }
    ],
    "health_suggestions": ["建议1", "建议2"],
    "follow_up": {
        "recommended_items": ["复查项目1", "复查项目2"],
        "recommended_time": "建议复查时间",
        "notes": "注意事项"
    }
}"""

            # 4. 调用 Kimi 分析
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请分析以下体检报告内容：\n\n{file_content}"}
            ]

            # 强制使用K2模型
            k2_model = "kimi-k2-0711-preview"
            response = await self.client.chat.completions.create(
                model=k2_model,
                messages=messages,
                temperature=0.2,  # 降低温度提高确定性
                max_tokens=8192,  # 增加 token 上限避免截断
                response_format={"type": "json_object"}
            )

            # 解析AI返回的JSON内容 - 增加清洗逻辑
            content = response.choices[0].message.content
            
            # 清理可能的 markdown 代码块和多余字符
            content = content.strip()
            
            # 移除开头的 ```json 或 ```
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
                
            # 移除结尾的 ```
            if content.endswith('```'):
                content = content[:-3]
                
            content = content.strip()
            
            # 记录原始内容用于调试
            logger.debug(f"AI返回内容（清洗后前500字符）: {content[:500]}...")
            
            try:
                analysis_result = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {str(e)}")
                logger.error(f"原始内容: {content[:2000]}")  # 记录更多内容用于排查
                raise Exception(f"AI返回内容格式错误: {str(e)}")
            
            analysis_result['file_id'] = file_id
            
            logger.info("医疗报告分析完成")
            return analysis_result

        except Exception as e:
            logger.error(f"医疗报告分析失败: {str(e)}")
            raise

    async def delete_file(self, file_id: str) -> bool:
        """
        删除已上传的文件

        Args:
            file_id: 文件ID

        Returns:
            是否删除成功
        """
        try:
            url = f"{self._base_url}/files/{file_id}"
            headers = {
                "Authorization": f"Bearer {self._api_key}"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(url, headers=headers)

                if response.status_code == 200:
                    logger.info(f"文件删除成功: {file_id}")
                    return True
                else:
                    logger.error(f"文件删除失败: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"文件删除异常: {str(e)}")
            return False


# 全局服务实例
kimi_service = MoonshotService()


# 依赖注入函数
async def get_kimi_service() -> MoonshotService:
    """获取Kimi服务实例"""
    return kimi_service
