"""
数据库模型定义
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Gunpla(db.Model):
    """高达模型信息表"""
    __tablename__ = 'gunpla'
    
    id = db.Column(db.Integer, primary_key=True)
    name_cn = db.Column(db.String(200), nullable=False, comment='中文名称')
    name_jp = db.Column(db.String(200), comment='日文名称')
    name_en = db.Column(db.String(200), comment='英文名称')
    grade = db.Column(db.String(50), nullable=False, comment='级别 (MG, RG, HGUC, HGGTO, HGBF/BD, EG, PG, SD, 成品, 国产盗版)')
    ms_number = db.Column(db.String(100), comment='机体编号')
    series = db.Column(db.String(200), comment='所属系列')
    subcategory = db.Column(db.String(100), comment='子分类 (普通版, 网络限定版, 其他限定版, EVANGELION系列, 勇者王系列, 参考出品等)')
    
    # 日本价格（日元）
    price_jp_msrp = db.Column(db.Float, comment='日本定价（日元）')
    price_jp_market = db.Column(db.Float, comment='日本市场价格（日元）')
    
    # 美国价格（美元）
    price_us_msrp = db.Column(db.Float, comment='美国定价（美元）')
    price_us_market = db.Column(db.Float, comment='美国市场价格（美元）')
    
    # 中国价格（人民币）
    price_cn_msrp = db.Column(db.Float, comment='中国定价（人民币）')
    price_cn_market = db.Column(db.Float, comment='中国市场价格（人民币）')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    wishlist_items = db.relationship('Wishlist', backref='gunpla', lazy=True, cascade='all, delete-orphan')
    collection_items = db.relationship('Collection', backref='gunpla', lazy=True, cascade='all, delete-orphan')
    price_history = db.relationship('PriceHistory', backref='gunpla', lazy=True, cascade='all, delete-orphan')
    
    def calculate_suan(self, jpy_to_cny_rate=20.0):
        """
        计算"算"数
        算 = (中国市场价格 / 日本定价) * 100
        例如：1000日元定价，卖100元人民币 = 10算
        """
        if self.price_jp_msrp and self.price_cn_market:
            # 将日元定价转换为人民币
            jp_yuan = self.price_jp_msrp / jpy_to_cny_rate
            if jp_yuan > 0:
                return round((self.price_cn_market / jp_yuan) * 100, 2)
        return None
    
    def to_dict(self):
        """转换为字典格式（用于JSON响应）"""
        return {
            'id': self.id,
            'name_cn': self.name_cn,
            'name_jp': self.name_jp,
            'name_en': self.name_en,
            'grade': self.grade,
            'ms_number': self.ms_number,
            'series': self.series,
            'subcategory': self.subcategory,
            'price_jp_msrp': self.price_jp_msrp,
            'price_jp_market': self.price_jp_market,
            'price_us_msrp': self.price_us_msrp,
            'price_us_market': self.price_us_market,
            'price_cn_msrp': self.price_cn_msrp,
            'price_cn_market': self.price_cn_market,
            'suan': self.calculate_suan()
        }
    
    def __repr__(self):
        return f'<Gunpla {self.name_cn}>'


class Wishlist(db.Model):
    """想要列表"""
    __tablename__ = 'wishlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='用户ID（可选，如果为None则为公共列表）')
    gunpla_id = db.Column(db.Integer, db.ForeignKey('gunpla.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, comment='备注')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'gunpla_id': self.gunpla_id,
            'gunpla': self.gunpla.to_dict() if self.gunpla else None,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Wishlist {self.gunpla_id}>'


class Collection(db.Model):
    """已购买列表"""
    __tablename__ = 'collection'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='用户ID（可选，如果为None则为公共列表）')
    gunpla_id = db.Column(db.Integer, db.ForeignKey('gunpla.id'), nullable=False)
    purchase_date = db.Column(db.Date, comment='购买日期')
    purchase_price = db.Column(db.Float, comment='购买价格')
    purchase_platform = db.Column(db.String(100), comment='购买平台')
    notes = db.Column(db.Text, comment='备注')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'gunpla_id': self.gunpla_id,
            'gunpla': self.gunpla.to_dict() if self.gunpla else None,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_price': self.purchase_price,
            'purchase_platform': self.purchase_platform,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Collection {self.gunpla_id}>'


class Coupon(db.Model):
    """优惠券表"""
    __tablename__ = 'coupons'
    
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(100), nullable=False, comment='平台（淘宝、拼多多等）')
    discount_type = db.Column(db.String(50), nullable=False, comment='折扣类型 (percentage, fixed_amount)')
    discount_value = db.Column(db.Float, nullable=False, comment='折扣值（百分比或固定金额）')
    max_discount = db.Column(db.Float, comment='最高减免金额')
    min_purchase = db.Column(db.Float, comment='最低购买金额')
    valid_from = db.Column(db.Date, comment='有效期开始')
    valid_until = db.Column(db.Date, comment='有效期结束')
    description = db.Column(db.Text, comment='描述')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_valid(self):
        """检查优惠券是否有效"""
        from datetime import date
        today = date.today()
        if self.valid_until and today > self.valid_until:
            return False
        if self.valid_from and today < self.valid_from:
            return False
        return True
    
    def calculate_discount(self, original_price):
        """
        计算优惠后的价格和节省金额
        返回: (final_price, savings, discount_rate)
        """
        if self.discount_type == 'percentage':
            # 百分比折扣
            discount = original_price * (self.discount_value / 100)
            if self.max_discount:
                discount = min(discount, self.max_discount)
        else:  # fixed_amount
            # 固定金额折扣
            discount = self.discount_value
        
        final_price = max(0, original_price - discount)
        savings = discount
        discount_rate = (savings / original_price * 100) if original_price > 0 else 0
        
        return {
            'final_price': round(final_price, 2),
            'savings': round(savings, 2),
            'discount_rate': round(discount_rate, 2)
        }
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'platform': self.platform,
            'discount_type': self.discount_type,
            'discount_value': self.discount_value,
            'max_discount': self.max_discount,
            'min_purchase': self.min_purchase,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'description': self.description,
            'is_valid': self.is_valid()
        }
    
    def __repr__(self):
        return f'<Coupon {self.platform} {self.discount_value}>'


class PriceHistory(db.Model):
    """价格历史表"""
    __tablename__ = 'price_history'
    
    id = db.Column(db.Integer, primary_key=True)
    gunpla_id = db.Column(db.Integer, db.ForeignKey('gunpla.id'), nullable=False)
    platform = db.Column(db.String(100), nullable=False, comment='平台（淘宝、拼多多）')
    price = db.Column(db.Float, nullable=False, comment='价格')
    url = db.Column(db.String(500), comment='商品链接')
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'gunpla_id': self.gunpla_id,
            'platform': self.platform,
            'price': self.price,
            'url': self.url,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }
    
    def __repr__(self):
        return f'<PriceHistory {self.gunpla_id} {self.platform} {self.price}>'


class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, comment='用户名')
    email = db.Column(db.String(120), unique=True, nullable=True, comment='邮箱')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    last_login = db.Column(db.DateTime, comment='最后登录时间')
    is_active = db.Column(db.Boolean, default=True, comment='是否激活')
    
    # 关联关系
    wishlist_items = db.relationship('Wishlist', backref='user', lazy=True, cascade='all, delete-orphan')
    collection_items = db.relationship('Collection', backref='user', lazy=True, cascade='all, delete-orphan')
    share_links = db.relationship('ShareLink', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Flask-Login需要的属性
    @property
    def is_authenticated(self):
        """用户是否已认证"""
        return True
    
    @property
    def is_anonymous(self):
        """是否为匿名用户"""
        return False
    
    def get_id(self):
        """获取用户ID（Flask-Login需要）"""
        return str(self.id)
    
    def set_password(self, password):
        """设置密码（使用Werkzeug的密码哈希）"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """检查密码"""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'


class ShareLink(db.Model):
    """分享链接表"""
    __tablename__ = 'share_links'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    list_type = db.Column(db.String(20), nullable=False, comment='列表类型 (wishlist, collection)')
    token = db.Column(db.String(64), unique=True, nullable=False, comment='分享令牌')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    expires_at = db.Column(db.DateTime, comment='过期时间（可选）')
    is_active = db.Column(db.Boolean, default=True, comment='是否有效')

    def __repr__(self):
        return f'<ShareLink {self.user_id} {self.list_type}>'

