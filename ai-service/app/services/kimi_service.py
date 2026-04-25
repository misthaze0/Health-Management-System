"""
Kimi (Moonshot) AI服务封装
提供与Moonshot API的交互功能，支持联网搜索、Token计算和文件分析
"""
import json
import asyncio
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

    # 别名方法，与stream_chat功能相同，用于兼容routes.py中的调用
    chat_stream = stream_chat

    async def chat_stream_with_tools(
        self,
        messages: List[Dict[str, str]],
        enable_web_search: bool = False,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """
        带工具调用的流式聊天（支持联网搜索）

        Args:
            messages: 消息列表
            enable_web_search: 是否启用联网搜索
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

            # 如果启用联网搜索，添加工具配置
            if enable_web_search:
                params["tools"] = [{"type": "web_search"}]

            stream_response = await self.client.chat.completions.create(**params)

            async for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"带工具流式聊天失败: {str(e)}")
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

        根据Moonshot API文档，使用 files.create API 上传文件。
        注意：目前文件上传接口仅支持 file-extract 一种 purpose 值。

        Args:
            file_path: 本地文件路径
            purpose: 文件用途，默认为 "file-extract"（提取内容）

        Returns:
            文件信息，包含文件ID
        """
        try:
            # 使用 OpenAI SDK 的 files.create 方法（符合Moonshot文档推荐）
            # client.files.create(file=Path(file_path), purpose="file-extract")
            from pathlib import Path
            file_object = await self.client.files.create(
                file=Path(file_path),
                purpose=purpose
            )

            # 转换为字典格式
            result = {
                'id': file_object.id,
                'object': file_object.object,
                'bytes': file_object.bytes,
                'created_at': file_object.created_at,
                'filename': file_object.filename,
                'purpose': file_object.purpose,
                'status': file_object.status,
                'status_details': file_object.status_details
            }

            logger.info(f"文件上传成功: {result.get('id')}")
            return result

        except Exception as e:
            logger.error(f"文件上传异常: {str(e)}")
            raise

    async def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        获取文件信息（包括处理状态）

        Args:
            file_id: 文件ID

        Returns:
            文件信息字典
        """
        try:
            file_info = await self.client.files.retrieve(file_id=file_id)
            return {
                'id': file_info.id,
                'status': file_info.status,
                'filename': file_info.filename,
                'bytes': file_info.bytes,
                'created_at': file_info.created_at
            }
        except Exception as e:
            logger.error(f"获取文件信息异常: {str(e)}")
            raise

    async def get_file_content(self, file_id: str) -> str:
        """
        获取已上传文件的内容（文本提取结果）

        根据Moonshot API文档，使用 files.content API 获取文件内容。
        注意：某些旧版本示例中的 retrieve_content API 在最新版本标记了 warning，
        应该使用 files.content(file_id=file_id).text

        Args:
            file_id: 文件ID

        Returns:
            文件内容文本
        """
        try:
            # 使用 OpenAI SDK 的 files.content 方法（符合Moonshot文档推荐）
            # client.files.content(file_id=file_id).text
            file_content_obj = await self.client.files.content(file_id=file_id)
            content = file_content_obj.text

            logger.info(f"文件内容获取成功: {file_id}, 内容长度: {len(content)} 字符")
            return content

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
            # 0. 先验证本地文件内容
            logger.info(f"开始验证文件: {file_path}")
            with open(file_path, 'rb') as f:
                file_header = f.read(100)

            # 检查文件是否是PDF格式 (PDF文件以 %PDF 开头)
            if file_header.startswith(b'%PDF'):
                logger.info(f"文件验证通过: 有效的PDF格式")
            elif file_header.startswith(b'<!DOCTYPE') or file_header.startswith(b'<html'):
                logger.error(f"文件验证失败: 上传的是HTML网页文件，不是PDF")
                raise Exception("上传的文件是HTML网页格式，请上传PDF格式的体检报告")
            else:
                # 尝试读取文件开头部分用于调试
                try:
                    header_text = file_header.decode('utf-8', errors='ignore')[:50]
                    logger.warning(f"文件格式未知，文件头内容: {header_text}")
                except:
                    pass

            # 1. 上传文件
            logger.info(f"开始上传医疗报告到Kimi API: {file_path}")
            file_info = await self.upload_file(file_path, purpose="file-extract")
            file_id = file_info.get('id')
            logger.info(f"文件上传成功，文件ID: {file_id}")

            # 2. 等待文件处理完成并获取内容（带重试机制）
            logger.info(f"等待Kimi API处理文件内容: {file_id}")
            file_content = None
            max_retries = 15
            retry_delay = 1  # 秒

            for attempt in range(max_retries):
                try:
                    # 先检查文件状态
                    file_info = await self.get_file_info(file_id)
                    file_status = file_info.get('status', '')
                    logger.info(f"文件状态: {file_status}")

                    # 如果文件还在处理中，等待
                    if file_status == 'processing':
                        logger.info(f"第 {attempt + 1}/{max_retries} 次尝试：文件正在处理中，等待 {retry_delay} 秒后重试...")
                        await asyncio.sleep(retry_delay)
                        continue

                    # 如果文件处理完成，获取内容
                    if file_status == 'ok':
                        file_content = await self.get_file_content(file_id)
                        if file_content and len(file_content.strip()) > 50:
                            logger.info(f"成功获取文件内容，长度: {len(file_content)} 字符")
                            break
                        else:
                            logger.warning(f"文件内容为空或过少")
                            break
                    else:
                        logger.warning(f"文件状态异常: {file_status}")
                        break

                except Exception as e:
                    logger.warning(f"第 {attempt + 1}/{max_retries} 次尝试失败: {str(e)}，等待 {retry_delay} 秒后重试...")
                    await asyncio.sleep(retry_delay)

            # 验证提取的内容
            if not file_content or len(file_content.strip()) < 50:
                logger.error(f"Kimi API提取的内容过少或为空")
                raise Exception("无法从PDF中提取有效文本内容，请检查PDF文件是否包含可提取的文本")

            # 检查提取的内容是否是HTML
            content_preview = file_content.strip()[:200].lower()
            if content_preview.startswith('<!doctype') or content_preview.startswith('<html'):
                logger.error(f"Kimi API提取的内容是HTML网页源码")
                raise Exception("提取的内容是网页源码，请上传正确的PDF体检报告文件")

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
            # 截取文件内容前3000字符，加快处理速度
            content_for_analysis = file_content[:3000] if len(file_content) > 3000 else file_content
            logger.info(f"准备调用Kimi AI分析，内容长度: {len(content_for_analysis)} 字符")

            # 按照Moonshot最佳实践：将文件内容作为system prompt放入请求中
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"体检报告内容如下：\n\n{content_for_analysis}"},
                {"role": "user", "content": "请根据以上体检报告内容，按照指定格式输出分析报告"}
            ]

            # 使用轻量级模型以提高响应速度
            fast_model = "moonshot-v1-8k"
            logger.info(f"开始调用Kimi API，模型: {fast_model}")

            # 添加重试机制处理429限流错误
            max_api_retries = 3
            api_retry_delay = 2  # 秒
            response = None

            for api_attempt in range(max_api_retries):
                try:
                    response = await self.client.chat.completions.create(
                        model=fast_model,
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1500,  # 降低token上限，加快响应
                        response_format={"type": "json_object"}
                    )
                    logger.info("Kimi API调用完成")
                    break
                except Exception as api_error:
                    error_str = str(api_error)
                    if "429" in error_str or "overloaded" in error_str.lower():
                        if api_attempt < max_api_retries - 1:
                            logger.warning(f"Kimi API限流(429)，第 {api_attempt + 1}/{max_api_retries} 次尝试失败，等待 {api_retry_delay} 秒后重试...")
                            await asyncio.sleep(api_retry_delay)
                            continue
                        else:
                            logger.error(f"Kimi API限流，已达到最大重试次数: {error_str}")
                            raise Exception("Kimi AI服务当前繁忙，请稍后重试")
                    else:
                        raise

            if response is None:
                raise Exception("Kimi API调用失败，无响应")

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

            # 清理已上传的文件，避免达到存储限制（每个用户最多1000个文件）
            try:
                await self.delete_file(file_id)
                logger.info(f"已清理上传的文件: {file_id}")
            except Exception as delete_error:
                logger.warning(f"清理文件失败（非关键错误）: {delete_error}")

            return analysis_result

        except Exception as e:
            logger.error(f"医疗报告分析失败: {str(e)}")
            # 尝试清理文件，即使分析失败
            if 'file_id' in locals():
                try:
                    await self.delete_file(file_id)
                    logger.info(f"已清理上传的文件（分析失败后）: {file_id}")
                except:
                    pass
            raise

    async def delete_file(self, file_id: str) -> bool:
        """
        删除已上传的文件

        根据Moonshot API文档，定期清理已上传的文件以释放存储空间。

        Args:
            file_id: 文件ID

        Returns:
            是否删除成功
        """
        try:
            # 使用 OpenAI SDK 的 files.delete 方法（符合Moonshot文档推荐）
            # client.files.delete(file_id=file_id)
            await self.client.files.delete(file_id=file_id)
            logger.info(f"文件删除成功: {file_id}")
            return True

        except Exception as e:
            logger.error(f"文件删除异常: {str(e)}")
            return False


# 全局服务实例
kimi_service = MoonshotService()


# 依赖注入函数
async def get_kimi_service() -> MoonshotService:
    """获取Kimi服务实例"""
    return kimi_service
