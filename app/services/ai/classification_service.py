import jieba
from collections import Counter
from app.services.ai.base_service import BaseAIService, ai_service_exception_handler
from app.models import Category
from app import db

class AIClassificationService(BaseAIService):
    """智能文档分类服务"""
    
    def __init__(self):
        super().__init__('文档分类')
        self.category_keywords = {}
        self.default_category = None
        self.category_cache = {}
    
    def initialize(self):
        """初始化分类服务"""
        try:
            print("开始初始化AI分类服务...")
            
            # 从数据库加载分类信息
            categories = Category.query.all()
            if not categories:
                print("数据库中未找到分类信息，使用默认分类配置")
                self._create_default_categories()
                categories = Category.query.all()
            
            # 构建分类关键词库
            self.category_keywords = self._build_category_keywords(categories)
            
            # 设置默认分类
            self.default_category = Category.query.filter_by(name='技术').first()
            
            # 初始化jieba
            jieba.initialize()
            
            self.initialized = True
            print(f"AI分类服务初始化完成，共加载 {len(categories)} 个分类")
            
        except Exception as e:
            print(f"AI分类服务初始化失败: {e}")
            self.initialized = False
    
    def _create_default_categories(self):
        """创建默认分类（如果数据库为空）"""
        default_categories = [
            {'name': '技术', 'description': '编程、开发、技术相关'},
            {'name': '学习', 'description': '学习笔记、知识总结'},
            {'name': '工作', 'description': '工作记录、项目管理'},
            {'name': '生活', 'description': '日常生活、个人思考'}
        ]
        
        for cat_data in default_categories:
            category = Category(**cat_data)
            db.session.add(category)
        
        db.session.commit()
        print("已创建默认分类")
    
    def _build_category_keywords(self, categories):
        """构建分类关键词库"""
        keywords_config = {
            '技术': {
                'keywords': [
                    '编程', '代码', '算法', 'Python', 'Java', 'JavaScript', '前端', '后端',
                    '数据库', 'MySQL', 'Redis', '架构', '开发', '技术', 'API', '框架',
                    '部署', '服务器', '网络', '安全', 'Docker', 'Linux', 'Git', '测试'
                ],
                'weight': 1.0
            },
            '学习': {
                'keywords': [
                    '学习', '笔记', '总结', '心得', '教程', '掌握', '理解', '知识点',
                    '方法', '技巧', '经验', '读书', '课程', '教育', '培训', '复习',
                    '练习', '掌握', '进步', '成长'
                ],
                'weight': 1.0
            },
            '工作': {
                'keywords': [
                    '工作', '项目', '任务', '会议', '汇报', '计划', '执行', '完成',
                    '团队', '协作', '管理', '进度', '目标', '绩效', '沟通', '协调',
                    '负责', '跟进', '总结', '复盘'
                ],
                'weight': 1.0
            },
            '生活': {
                'keywords': [
                    '生活', '日常', '记录', '思考', '感悟', '体验', '分享', '旅行',
                    '美食', '健康', '运动', '娱乐', '家庭', '朋友', '心情', '计划',
                    '目标', '阅读', '电影', '音乐'
                ],
                'weight': 1.0
            }
        }
        
        category_keywords = {}
        for category in categories:
            if category.name in keywords_config:
                category_keywords[category.id] = keywords_config[category.name]
        
        return category_keywords
    
    @ai_service_exception_handler
    def predict_category(self, title, content):
        """预测文档分类"""
        self.ensure_initialized()
        
        # 生成缓存键
        cache_key = f"{title[:50]}_{hash(content) % 10000}"
        if cache_key in self.category_cache:
            return self.category_cache[cache_key]
        
        if not self.category_keywords:
            result = self._fallback_category_result()
            self.category_cache[cache_key] = result
            return result
        
        # 合并文本进行分析
        text = f"{title} {content}"
        words = jieba.lcut(text)
        word_freq = Counter(words)
        
        # 计算每个分类的得分
        category_scores = {}
        for category_id, config in self.category_keywords.items():
            score = 0
            for keyword in config['keywords']:
                if keyword in word_freq:
                    score += word_freq[keyword] * config['weight']
            
            # 标题关键词权重加倍
            title_words = jieba.lcut(title)
            title_freq = Counter(title_words)
            for keyword in config['keywords']:
                if keyword in title_freq:
                    score += title_freq[keyword] * config['weight'] * 2
            
            category_scores[category_id] = score
        
        # 选择最佳分类
        best_category_id = None
        confidence = 0.0
        
        if category_scores:
            best_category_id, best_score = max(category_scores.items(), key=lambda x: x[1])
            total_score = sum(category_scores.values())
            confidence = best_score / total_score if total_score > 0 else 0.0
            
            # 置信度阈值
            if confidence < 0.3:
                best_category_id = self.default_category.id if self.default_category else None
                confidence = 0.3
        
        result = {
            'success': True,
            'category_id': best_category_id,
            'confidence': round(confidence, 3),
            'method': 'keyword_matching',
            'scores': category_scores
        }
        
        self.category_cache[cache_key] = result
        return result
    
    def _fallback_category_result(self):
        """分类服务的降级方案"""
        default_id = self.default_category.id if self.default_category else None
        return {
            'success': False,
            'category_id': default_id,
            'confidence': 0.5,
            'method': 'fallback',
            'fallback': True
        }
    
    def process(self, text, **kwargs):
        """处理文本分类"""
        title = kwargs.get('title', '')
        content = kwargs.get('content', text)
        return self.predict_category(title, content)

# 创建全局实例
classification_service = AIClassificationService()
