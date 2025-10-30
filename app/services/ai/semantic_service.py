import jieba
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.ai.base_service import BaseAIService, ai_service_exception_handler

class SemanticService(BaseAIService):
    """语义搜索服务"""
    
    def __init__(self):
        super().__init__('语义搜索')
        self.vectorizer = None
        self.semantic_cache = {}
    
    def initialize(self):
        """初始化语义搜索服务"""
        try:
            print("开始初始化语义搜索服务...")
            
            # 初始化jieba
            jieba.initialize()
            
            # 初始化TF-IDF向量化器
            self.vectorizer = TfidfVectorizer(
                tokenizer=jieba.lcut,
                max_features=500,
                min_df=1,
                max_df=0.9
            )
            
            self.initialized = True
            print("语义搜索服务初始化完成")
            
        except Exception as e:
            print(f"语义搜索服务初始化失败: {e}")
            self.initialized = False
    
    @ai_service_exception_handler
    def semantic_similarity(self, text1, text2):
        """计算两个文本的语义相似度"""
        self.ensure_initialized()
        
        if not text1 or not text2:
            return {
                'success': False,
                'similarity': 0.0,
                'error': '输入文本为空'
            }
        
        cache_key = f"{hash(text1)}_{hash(text2)}"
        if cache_key in self.semantic_cache:
            return self.semantic_cache[cache_key]
        
        try:
            # 使用TF-IDF计算相似度
            texts = [text1, text2]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            result = {
                'success': True,
                'similarity': round(float(similarity), 4),
                'method': 'tfidf_cosine',
                'text1_preview': text1[:50] + '...' if len(text1) > 50 else text1,
                'text2_preview': text2[:50] + '...' if len(text2) > 50 else text2
            }
            
            self.semantic_cache[cache_key] = result
            return result
            
        except Exception as e:
            print(f"语义相似度计算失败: {e}")
            return self._fallback_similarity(text1, text2)
    
    def _fallback_similarity(self, text1, text2):
        """语义相似度的降级方案"""
        try:
            words1 = set(jieba.lcut(text1))
            words2 = set(jieba.lcut(text2))
            
            if not words1 or not words2:
                similarity = 0.0
            else:
                intersection = words1.intersection(words2)
                union = words1.union(words2)
                similarity = len(intersection) / len(union)
            
            return {
                'success': False,
                'similarity': round(similarity, 4),
                'method': 'jaccard_fallback',
                'fallback': True
            }
        except Exception as e:
            print(f"降级相似度计算也失败了: {e}")
            return {
                'success': False,
                'similarity': 0.0,
                'method': 'failed'
            }
    
    def process(self, text, **kwargs):
        """处理语义搜索请求"""
        comparison_text = kwargs.get('comparison_text')
        
        if comparison_text:
            return self.semantic_similarity(text, comparison_text)
        else:
            return {
                'success': False,
                'error': '需要提供comparison_text参数'
            }

# 创建全局实例
semantic_service = SemanticService()
