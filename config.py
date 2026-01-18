"""
配置文件
"""
import os

# 项目根目录
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """应用配置类"""
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = database_url or \
        'sqlite:///' + os.path.join(basedir, 'gunpla.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 汇率配置（可根据需要调整）
    JPY_TO_CNY_RATE = 20.0  # 1人民币 = 20日元（示例汇率，建议使用实时汇率API）
    JPY_TO_USD_RATE = 150.0  # 1美元 = 150日元（示例汇率，建议使用实时汇率API）
    
    # 反向汇率（用于换算）
    CNY_TO_JPY_RATE = 1.0 / JPY_TO_CNY_RATE  # 1日元 = 0.05人民币
    USD_TO_JPY_RATE = 1.0 / JPY_TO_USD_RATE  # 1日元 = 0.0067美元

