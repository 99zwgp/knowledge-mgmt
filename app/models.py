from app import db
from datetime import datetime
import json

class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.String(50), default='text')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    tags = db.Column(db.JSON)  # 存储标签列表
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 添加索引
    __table_args__ = (
        db.Index('idx_document_created', 'created_at'),
        db.Index('idx_document_category', 'category_id'),
    )
    
    def to_dict(self):
        data = {
            'id': self.id,
            'title': self.title,
            'content': self.content[:200] + '...' if len(self.content) > 200 else self.content,
            'file_type': self.file_type,
            'tags': self.tags or [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if self.category:
            data['category'] = {
                'id': self.category.id,
                'name': self.category.name
            }
        
        return data
    
    def __repr__(self):
        return f'<Document {self.id}: {self.title}>'

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    documents = db.relationship('Document', backref='category', lazy=True)
    
    # 添加索引
    __table_args__ = (
        db.Index('idx_category_name', 'name'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'document_count': len(self.documents)
        }
    
    def __repr__(self):
        return f'<Category {self.id}: {self.name}>'
