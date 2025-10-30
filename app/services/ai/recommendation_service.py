import jieba
import numpy as np
from collections import Counter, defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.ai.base_service import BaseAIService, ai_service_exception_handler
from app.models import Document
from app import db

class RecommendationService(BaseAIService):
    """内容推荐服务"""
    
    def __init__(self):
        super().__init__('内容推荐')
        self.vectorizer = None
        self.document_vectors = None
        self.document_ids = []
        self.similarity_cache = {}
    
    def initialize(self):
        """初始化推荐服务"""
        try:
            print("开始初始化推荐服务...")
            
            # 初始化jieba
            jieba.initialize()
            
            # 初始化TF-IDF向量化器
            self.vectorizer = TfidfVectorizer(
                tokenizer=jieba.lcut,
                max_features=1000,
                min_df=1,
                max_df=0.8
            )
            
            # 预加载文档数据
            self._load_documents()
            
            self.initialized = True
            print(f"推荐服务初始化完成，共加载 {len(self.document_ids)} 个文档")
            
        except Exception as e:
            print(f"推荐服务初始化失败: {e}")
            self.initialized = False
    
    def _load_documents(self):
        """加载文档数据并构建向量空间"""
        try:
            documents = Document.query.filter(
                Document.content.isnot(None),
                Document.content != ''
            ).all()
            
            if not documents:
                print("没有找到可用的文档数据")
                return
            
            self.document_ids = [doc.id for doc in documents]
            document_texts = [
                f"{doc.title} {doc.content}" for doc in documents
            ]
            
            # 构建TF-IDF向量
            if document_texts:
                self.document_vectors = self.vectorizer.fit_transform(document_texts)
            else:
                self.document_vectors = None
                
        except Exception as e:
            print(f"加载文档数据失败: {e}")
            self.document_vectors = None
    
    @ai_service_exception_handler
    def recommend_similar_documents(self, document_id, top_k=5):
        """推荐相似文档"""
        self.ensure_initialized()
        
        # 检查是否有足够的文档数据
        if self.document_vectors is None or len(self.document_ids) < 2:
            return {
                'success': True,
                'recommendations': [],
                'method': 'insufficient_data',
                'count': 0
            }
        
        # 检查缓存
        cache_key = f"{document_id}_{top_k}"
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        try:
            # 查找目标文档的索引
            if document_id not in self.document_ids:
                return {
                    'success': False,
                    'error': '文档不存在',
                    'recommendations': []
                }
            
            target_idx = self.document_ids.index(document_id)
            
            # 计算相似度 - 修复numpy数组比较问题
            if hasattr(self.document_vectors, 'shape') and self.document_vectors.shape[0] > 1:
                similarities = cosine_similarity(
                    self.document_vectors[target_idx:target_idx+1],
                    self.document_vectors
                ).flatten()
            else:
                return {
                    'success': True,
                    'recommendations': [],
                    'method': 'insufficient_vectors',
                    'count': 0
                }
            
            # 排除自己，获取最相似的文档
            similar_indices = np.argsort(similarities)[::-1]
            recommendations = []
            
            for idx in similar_indices:
                if idx == target_idx:  # 跳过自己
                    continue
                
                if len(recommendations) >= top_k:
                    break
                
                doc_id = self.document_ids[idx]
                similarity_score = float(similarities[idx])
                
                # 只保留相似度较高的推荐
                if similarity_score > 0.1:
                    document = Document.query.get(doc_id)
                    if document:
                        recommendations.append({
                            'document_id': doc_id,
                            'title': document.title,
                            'similarity': round(similarity_score, 3),
                            'category_id': document.category_id,
                            'tags': document.tags or []
                        })
            
            result = {
                'success': True,
                'recommendations': recommendations,
                'method': 'cosine_similarity',
                'count': len(recommendations),
                'target_document_id': document_id
            }
            
            # 缓存结果
            self.similarity_cache[cache_key] = result
            return result
            
        except Exception as e:
            print(f"文档推荐失败: {e}")
            return self._fallback_recommendations(document_id, top_k)
    
    def recommend_by_content(self, content, top_k=5):
        """基于内容推荐文档"""
        self.ensure_initialized()
        
        # 检查文档数据
        if self.document_vectors is None or not self.document_ids:
            return {
                'success': True,
                'recommendations': [],
                'method': 'no_documents',
                'count': 0
            }
        
        try:
            # 将查询内容向量化
            query_vector = self.vectorizer.transform([content])
            
            # 计算相似度 - 修复numpy数组比较问题
            if hasattr(self.document_vectors, 'shape') and self.document_vectors.shape[0] > 0:
                similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
            else:
                return {
                    'success': True,
                    'recommendations': [],
                    'method': 'no_vector_data',
                    'count': 0
                }
            
            # 获取最相似的文档
            similar_indices = np.argsort(similarities)[::-1]
            recommendations = []
            
            for idx in similar_indices:
                if len(recommendations) >= top_k:
                    break
                
                doc_id = self.document_ids[idx]
                similarity_score = float(similarities[idx])
                
                if similarity_score > 0.1:
                    document = Document.query.get(doc_id)
                    if document:
                        recommendations.append({
                            'document_id': doc_id,
                            'title': document.title,
                            'similarity': round(similarity_score, 3),
                            'category_id': document.category_id,
                            'tags': document.tags or []
                        })
            
            return {
                'success': True,
                'recommendations': recommendations,
                'method': 'content_based',
                'count': len(recommendations),
                'query_content_preview': content[:100] + '...' if len(content) > 100 else content
            }
            
        except Exception as e:
            print(f"基于内容推荐失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'recommendations': [],
                'method': 'content_based_failed'
            }
    
    def _fallback_recommendations(self, document_id, top_k):
        """推荐服务的降级方案"""
        try:
            # 基于分类的简单推荐
            target_doc = Document.query.get(document_id)
            if not target_doc:
                return {
                    'success': False,
                    'recommendations': [],
                    'method': 'fallback_failed'
                }
            
            # 查找同分类的文档
            similar_docs = Document.query.filter(
                Document.id != document_id,
                Document.category_id == target_doc.category_id
            ).order_by(Document.created_at.desc()).limit(top_k).all()
            
            recommendations = []
            for doc in similar_docs:
                recommendations.append({
                    'document_id': doc.id,
                    'title': doc.title,
                    'similarity': 0.5,
                    'category_id': doc.category_id,
                    'tags': doc.tags or [],
                    'method': 'category_based'
                })
            
            return {
                'success': True,
                'recommendations': recommendations,
                'method': 'category_fallback',
                'count': len(recommendations),
                'fallback': True
            }
            
        except Exception as e:
            print(f"降级推荐也失败了: {e}")
            return {
                'success': False,
                'recommendations': [],
                'method': 'fallback_failed'
            }
    
    def process(self, text, **kwargs):
        """处理推荐请求"""
        document_id = kwargs.get('document_id')
        if document_id:
            return self.recommend_similar_documents(document_id, kwargs.get('top_k', 5))
        else:
            return self.recommend_by_content(text, kwargs.get('top_k', 5))

# 创建全局实例
recommendation_service = RecommendationService()
