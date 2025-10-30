from flask import Blueprint, render_template

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def home():
    """显示前端看板主页"""
    return render_template('dashboard.html')
