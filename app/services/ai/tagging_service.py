import jieba
import jieba.analyse
from collections import Counter
import re
from app.services.ai.base_service import BaseAIService, ai_service_exception_handler

class AITaggingService(BaseAIService):
    """自动标签生成服务"""
    
    def __init__(self):
        super().__init__('标签生成')
        self.stop_words = self._load_stop_words()
        self.custom_dict_initialized = False
    
    def _load_stop_words(self):
        """加载中文停用词"""
        return {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '他', '她', '它', '我们', '你们', '他们', '这个', '那个'
        }
    
    def initialize(self):
        """初始化标签服务"""
        try:
            print("开始初始化AI标签服务...")
            
            # 初始化jieba
            jieba.initialize()
            self._setup_custom_dictionary()
            
            self.initialized = True
            print("AI标签服务初始化完成")
            
        except Exception as e:
            print(f"AI标签服务初始化失败: {e}")
            self.initialized = False
    
    def _setup_custom_dictionary(self):
        """设置自定义词典"""
        if self.custom_dict_initialized:
            return
            
        # 技术相关词汇
        tech_words = [
            'Python', 'Java', 'JavaScript', 'Vue', 'React', 'Flask', 'Django',
            'MySQL', 'Redis', 'Docker', 'Kubernetes', '机器学习', '深度学习',
            '人工智能', 'AI', '大数据', '云计算', '微服务', 'API', 'RESTful',
            '前端', '后端', '全栈', 'DevOps', 'Git', 'Linux', '算法', '数据结构'
        ]
        
        for word in tech_words:
            jieba.add_word(word, freq=1000)
        
        self.custom_dict_initialized = True
    
    @ai_service_exception_handler
    def extract_tags(self, text, top_k=8):
        """提取关键词标签"""
        self.ensure_initialized()
        
        if not text or len(text.strip()) < 10:
            return {
                'success': True,
                'tags': [],
                'method': 'skip_short_text',
                'tags_count': 0
            }
        
        try:
            # 方法1: TF-IDF
            keywords_tfidf = jieba.analyse.extract_tags(
                text, 
                topK=top_k * 2,
                withWeight=False,
                allowPOS=('n', 'vn', 'v', 'ns', 'nr', 'eng')
            )
            
            # 方法2: TextRank
            keywords_textrank = jieba.analyse.textrank(
                text,
                topK=top_k * 2,
                withWeight=False,
                allowPOS=('n', 'vn', 'v', 'ns', 'nr', 'eng')
            )
            
            # 方法3: 词频统计（兜底）
            frequency_tags = self._extract_by_frequency(text, top_k)
            
            # 融合算法结果
            all_keywords = []
            seen = set()
            
            # 优先TF-IDF结果
            for kw in keywords_tfidf:
                if kw not in seen and self._is_valid_tag(kw):
                    seen.add(kw)
                    all_keywords.append(('tfidf', kw))
            
            # 补充TextRank结果
            for kw in keywords_textrank:
                if kw not in seen and self._is_valid_tag(kw):
                    seen.add(kw)
                    all_keywords.append(('textrank', kw))
            
            # 如果结果不足，使用词频结果
            if len(all_keywords) < top_k:
                for kw in frequency_tags:
                    if kw not in seen and self._is_valid_tag(kw):
                        seen.add(kw)
                        all_keywords.append(('frequency', kw))
            
            # 取前top_k个
            final_tags = [kw for _, kw in all_keywords[:top_k]]
            
            return {
                'success': True,
                'tags': final_tags,
                'method': 'multi_algorithm_fusion',
                'tags_count': len(final_tags),
                'algorithms_used': list(set([algo for algo, _ in all_keywords[:top_k]]))
            }
            
        except Exception as e:
            print(f"标签提取失败，使用词频兜底: {e}")
            return self._fallback_tag_extraction(text, top_k)
    
    def _extract_by_frequency(self, text, top_k):
        """基于词频提取标签"""
        words = jieba.lcut(text)
        
        # 过滤有效词汇
        valid_words = []
        for word in words:
            if (len(word) > 1 and 
                word not in self.stop_words and
                not re.match(r'^\d+$', word) and
                not re.match(r'^[^\u4e00-\u9fa5a-zA-Z]+$', word) and
                self._is_valid_tag(word)):
                valid_words.append(word)
        
        # 统计词频
        word_freq = Counter(valid_words)
        return [word for word, _ in word_freq.most_common(top_k)]
    
    def _is_valid_tag(self, word):
        """检查是否为有效的标签"""
        if len(word) <= 1:
            return False
        if word in self.stop_words:
            return False
        if re.match(r'^\d+$', word):
            return False
        if re.match(r'^[^\u4e00-\u9fa5a-zA-Z]+$', word):
            return False
        return True
    
    def _fallback_tag_extraction(self, text, top_k):
        """标签提取的降级方案"""
        simple_tags = self._extract_by_frequency(text, top_k)
        return {
            'success': False,
            'tags': simple_tags,
            'method': 'frequency_fallback',
            'tags_count': len(simple_tags),
            'fallback': True
        }
    
    def generate_tags(self, title, content, existing_tags=None):
        """生成文档标签"""
        # 增强标题权重
        enhanced_text = f"{title} {title} {content}"
        
        result = self.extract_tags(enhanced_text, top_k=8)
        
        # 合并现有标签
        if existing_tags and result['success']:
            all_tags = list(set(existing_tags + result['tags']))
            result['tags'] = all_tags[:10]
            result['tags_count'] = len(result['tags'])
            result['merged_with_existing'] = True
        
        return result
    
    def process(self, text, **kwargs):
        """处理文本标签生成"""
        title = kwargs.get('title', '')
        content = kwargs.get('content', text)
        existing_tags = kwargs.get('existing_tags', [])
        
        return self.generate_tags(title, content, existing_tags)

# 创建全局实例
tagging_service = AITaggingService()
