"""
多模态输出模块
提供文档生成、语音合成和语音识别功能
"""

from .document_generator import DocumentGenerator, get_document_generator, generate_health_report
from .voice_synthesizer import VoiceSynthesizer, get_voice_synthesizer, synthesize_speech
from .voice_recognition import VoiceRecognizer, create_recognizer, recognize_file, recognize_bytes

__all__ = [
    # 文档生成
    'DocumentGenerator',
    'get_document_generator',
    'generate_health_report',
    # 语音合成
    'VoiceSynthesizer',
    'get_voice_synthesizer',
    'synthesize_speech',
    # 语音识别
    'VoiceRecognizer',
    'create_recognizer',
    'recognize_file',
    'recognize_bytes',
]
