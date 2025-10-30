import jieba
import jieba.analyse
from collections import Counter
import time
from datetime import datetime
from app.services.ai.base_service import BaseAIService, ai_service_exception_handler
from app.models import Category
from app import db

class RobustClassificationService(BaseAIService):
    """增强版智能文档分类服务 - 包含多算法融合和性能监控"""
    
    def __init__(self):
        super().__init__('增强文档分类')
        self.category_keywords = {}
        self.default_category = None
        self.category_cache = {}
        
        # 性能监控数据
        self.performance_stats = {
            'total_requests': 0,
            'successful_predictions': 0,
            'fallback_used': 0,
            'avg_processing_time': 0,
            'cache_hits': 0
        }
        
        # 多算法权重配置
        self.algorithm_weights = {
            'keyword_matching': 0.4,
            'tfidf_similarity': 0.3,
            'keyphrase_analysis': 0.3
        }
    
    def initialize(self):
        """初始化增强分类服务"""
        try:
            print("开始初始化增强AI分类服务...")
            
            # 从数据库加载分类信息
            categories = Category.query.all()
            if not categories:
                print("数据库中未找到分类信息，使用默认分类配置")
                self._create_default_categories()
                categories = Category.query.all()
            
            # 构建增强分类关键词库
            self.category_keywords = self._build_enhanced_category_keywords(categories)
            
            # 设置默认分类
            self.default_category = Category.query.filter_by(name='技术').first()
            
            # 初始化jieba
            jieba.initialize()
            
            # 加载停用词（可选）
            try:
                jieba.analyse.set_stop_words('app/services/ai/stop_words.txt')
            except:
                print("未找到停用词文件，使用默认配置")
            
            self.initialized = True
            print(f"增强AI分类服务初始化完成，共加载 {len(categories)} 个分类")
            
        except Exception as e:
            print(f"增强AI分类服务初始化失败: {e}")
            self.initialized = False
    
    def _build_enhanced_category_keywords(self, categories):
        """构建增强分类关键词库 - 更丰富的关键词和权重"""
        enhanced_keywords_config = {
            '技术': {
                'keywords': [
                    '编程', '代码', '算法', 'Python', 'Java', 'JavaScript', '前端', '后端',
                    '数据库', 'MySQL', 'Redis', '架构', '开发', '技术', 'API', '框架',
                    '部署', '服务器', '网络', '安全', 'Docker', 'Linux', 'Git', '测试',
                    '函数', '类', '对象', '模块', '包', '库', '接口', '协议', '编译', '调试'
                ],
                'weight': 1.2,  # 技术类权重稍高
                'priority_keywords': ['编程', '代码', '算法', 'Python']  # 高优先级关键词
            },
            '学习': {
                'keywords': [
                    '学习', '笔记', '总结', '心得', '教程', '掌握', '理解', '知识点',
                    '方法', '技巧', '经验', '读书', '课程', '教育', '培训', '复习',
                    '练习', '掌握', '进步', '成长', '概念', '原理', '理论', '实践'
                ],
                'weight': 1.0,
                'priority_keywords': ['学习', '笔记', '教程', '掌握']
            },
            '工作': {
                'keywords': [
                    '工作', '项目', '任务', '会议', '汇报', '计划', '执行', '完成',
                    '团队', '协作', '管理', '进度', '目标', '绩效', '沟通', '协调',
                    '负责', '跟进', '总结', '复盘', ' deadline', '里程碑', '交付', '评审'
                ],
                'weight': 1.1,
                'priority_keywords': ['项目', '任务', '会议', '计划']
            },
            '生活': {
                'keywords': [
                    '生活', '日常', '记录', '思考', '感悟', '体验', '分享', '旅行',
                    '美食', '健康', '运动', '娱乐', '家庭', '朋友', '心情', '计划',
                    '目标', '阅读', '电影', '音乐', '周末', '假期', '放松', '兴趣'
                ],
                'weight': 1.0,
                'priority_keywords': ['生活', '日常', '旅行', '健康']
            }
        }
        
        category_keywords = {}
        for category in categories:
            if category.name in enhanced_keywords_config:
                category_keywords[category.id] = enhanced_keywords_config[category.name]
        
        return category_keywords
    
    @ai_service_exception_handler
    def predict_category(self, title, content):
        """增强版分类预测 - 多算法融合"""
        self.ensure_initialized()
        
        start_time = time.time()
        self.performance_stats['total_requests'] += 1
        
        # 生成缓存键
        cache_key = f"{title[:50]}_{hash(content) % 10000}"
        if cache_key in self.category_cache:
            self.performance_stats['cache_hits'] += 1
            return self.category_cache[cache_key]
        
        if not self.category_keywords:
            result = self._fallback_category_result()
            self.category_cache[cache_key] = result
            return result
        
        # 方法1: 关键词匹配
        keyword_result = self._keyword_based_classification(title, content)
        
        # 方法2: 关键短语分析
        keyphrase_result = self._keyphrase_based_classification(title, content)
        
        # 方法3: 相似度分析（简化版）
        similarity_result = self._similarity_based_classification(title, content)
        
        # 多算法结果融合
        final_result = self._merge_algorithm_results(
            keyword_result, keyphrase_result, similarity_result
        )
        
        # 更新性能统计
        processing_time = time.time() - start_time
        self._update_performance_stats(success=True, processing_time=processing_time)
        
        # 缓存结果
        final_result['processing_time'] = round(processing_time, 3)
        self.category_cache[cache_key] = final_result
        
        return final_result
    
    def _keyword_based_classification(self, title, content):
        """基于关键词的分类（原有算法增强）"""
        text = f"{title} {content}"
        words = jieba.lcut(text)
        word_freq = Counter(words)
        
        category_scores = {}
        for category_id, config in self.category_keywords.items():
            score = 0
            
            # 普通关键词匹配
            for keyword in config['keywords']:
                if keyword in word_freq:
                    score += word_freq[keyword] * config['weight']
            
            # 高优先级关键词额外加分
            for p_keyword in config.get('priority_keywords', []):
                if p_keyword in word_freq:
                    score += word_freq[p_keyword] * config['weight'] * 1.5
            
            # 标题关键词权重加倍
            title_words = jieba.lcut(title)
            title_freq = Counter(title_words)
            for keyword in config['keywords']:
                if keyword in title_freq:
                    score += title_freq[keyword] * config['weight'] * 2
            
            category_scores[category_id] = score
        
        return {
            'method': 'keyword_matching',
            'scores': category_scores,
            'weight': self.algorithm_weights['keyword_matching']
        }
    
    def _keyphrase_based_classification(self, title, content):
        """基于关键短语的分类"""
        try:
            text = f"{title} {content}"
            
            # 提取关键短语
            keyphrases = jieba.analyse.extract_tags(text, topK=10, withWeight=True)
            
            category_scores = {}
            for category_id, config in self.category_keywords.items():
                score = 0
                
                for phrase, weight in keyphrases:
                    if phrase in config['keywords']:
                        # 关键短语的权重更高
                        score += weight * 2 * config['weight']
                
                category_scores[category_id] = score
            
            return {
                'method': 'keyphrase_analysis',
                'scores': category_scores,
                'weight': self.algorithm_weights['keyphrase_analysis']
            }
            
        except Exception as e:
            print(f"关键短语分析失败: {e}")
            return self._fallback_algorithm_result()
    
    def _similarity_based_classification(self, title, content):
        """基于相似度的分类（简化版）"""
        # 这里可以实现更复杂的相似度计算
        # 暂时使用关键词匹配的变体
        return self._keyword_based_classification(title, content)
    
    def _merge_algorithm_results(self, result1, result2, result3):
        """合并多个算法结果"""
        all_scores = {}
        
        # 收集所有算法的分数
        algorithms = [result1, result2, result3]
        
        for algorithm in algorithms:
            if algorithm['scores']:
                weight = algorithm['weight']
                for category_id, score in algorithm['scores'].items():
                    if category_id not in all_scores:
                        all_scores[category_id] = 0
                    all_scores[category_id] += score * weight
        
        # 选择最佳分类
        best_category_id = None
        confidence = 0.0
        
        if all_scores:
            best_category_id, best_score = max(all_scores.items(), key=lambda x: x[1])
            total_score = sum(all_scores.values())
            confidence = best_score / total_score if total_score > 0 else 0.0
            
            # 动态置信度阈值
            min_confidence = 0.25
            if confidence < min_confidence:
                best_category_id = self.default_category.id if self.default_category else None
                confidence = min_confidence
        
        return {
            'success': True,
            'category_id': best_category_id,
            'confidence': round(confidence, 3),
            'method': 'multi_algorithm_fusion',
            'algorithm_details': {
                'keyword_matching': result1['scores'],
                'keyphrase_analysis': result2['scores'],
                'similarity_analysis': result3['scores']
            },
            'final_scores': all_scores
        }
    
    def _fallback_algorithm_result(self):
        """算法降级结果"""
        return {
            'method': 'fallback',
            'scores': {},
            'weight': 0.1
        }
    
    def _fallback_category_result(self):
        """分类服务的降级方案"""
        default_id = self.default_category.id if self.default_category else None
        self.performance_stats['fallback_used'] += 1
        return {
            'success': False,
            'category_id': default_id,
            'confidence': 0.5,
            'method': 'fallback',
            'fallback': True
        }
    
    def _update_performance_stats(self, success, processing_time):
        """更新性能统计"""
        if success:
            self.performance_stats['successful_predictions'] += 1
        
        # 更新平均处理时间
        total_time = self.performance_stats['avg_processing_time'] * (self.performance_stats['total_requests'] - 1)
        self.performance_stats['avg_processing_time'] = (total_time + processing_time) / self.performance_stats['total_requests']
    
    def get_performance_report(self):
        """获取性能报告"""
        success_rate = (self.performance_stats['successful_predictions'] / self.performance_stats['total_requests']) * 100
        cache_hit_rate = (self.performance_stats['cache_hits'] / self.performance_stats['total_requests']) * 100
        
        return {
            'total_requests': self.performance_stats['total_requests'],
            'success_rate': round(success_rate, 2),
            'cache_hit_rate': round(cache_hit_rate, 2),
            'fallback_used': self.performance_stats['fallback_used'],
            'avg_processing_time': round(self.performance_stats['avg_processing_time'], 3),
            'initialized': self.initialized
        }
    
    def clear_cache(self):
        """清空缓存"""
        self.category_cache.clear()
        print("分类缓存已清空")
    
    def process(self, text, **kwargs):
        """处理文本分类"""
        title = kwargs.get('title', '')
        content = kwargs.get('content', text)
        return self.predict_category(title, content)

# 创建全局实例
robust_classification_service = RobustClassificationService()
