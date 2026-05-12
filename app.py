"""
高达价格查询工具 - Flask主应用
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Gunpla, Wishlist, Collection, Coupon, PriceHistory, User, ShareLink
from config import Config
from datetime import datetime, date
from urllib.parse import urljoin, urlparse
import csv
import io
import secrets
import os

app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)

# 初始化Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问此页面。'
login_manager.login_message_category = 'info'

SUPPORTED_LANGUAGES = {'zh', 'en'}
TRANSLATIONS_EN = {
    # Base template UI
    '高达价格查询工具': 'Gunpla Price Tool',
    '高达价格工具': 'Gunpla Price Tool',
    '高达列表': 'Gunpla List',
    '添加高达': 'Add Gunpla',
    '想要列表': 'Wishlist',
    '已购买': 'Collection',
    '优惠券': 'Coupons',
    '登出': 'Logout',
    '登录': 'Login',
    '注册': 'Register',
    '语言': 'Language',
    '中文': 'Chinese',
    '英文': 'English',
    '首页': 'Home',
    '用户登录': 'User Login',
    '用户注册': 'User Registration',
    '用户名': 'Username',
    '密码': 'Password',
    '记住我': 'Remember me',
    '还没有账号？立即注册': "Don't have an account? Register now",
    '已有账号？立即登录': 'Already have an account? Log in now',
    '邮箱（可选）': 'Email (optional)',
    '确认密码': 'Confirm password',
    '至少3个字符': 'At least 3 characters',
    '至少6个字符': 'At least 6 characters',
    '管理您的高达收藏，查询价格，分析优惠券': 'Manage your Gunpla collection, check prices, and analyze coupons.',
    '查看所有高达信息，包括多地区价格和"算"数计算': 'View all Gunpla info, including multi-region prices and conversion metrics.',
    '管理您想要购买的高达': 'Manage Gunpla you plan to buy.',
    '记录您已购买的高达': 'Track Gunpla you have purchased.',
    '查看列表': 'View List',
    '添加新的高达信息到数据库': 'Add new Gunpla records to the database.',
    '优惠券管理': 'Coupon Management',
    '管理优惠券并分析最适合的高达': 'Manage coupons and analyze the best matches for your Gunpla.',
    '查看优惠券': 'View Coupons',
    '高达详情': 'Gunpla Details',
    '详情': 'Details',
    '搜索名称或编号...': 'Search by name or model number...',
    '全部级别': 'All Grades',
    '全部子分类': 'All Subcategories',
    '搜索': 'Search',
    '名称': 'Name',
    '级别': 'Grade',
    '子分类': 'Subcategory',
    '日本定价': 'Japan MSRP',
    '中国市场价': 'China Market Price',
    '算': 'Rate',
    '操作': 'Actions',
    '暂无数据': 'No Data',
    '还没有添加任何高达，': 'No Gunpla added yet, ',
    '点击这里添加第一个': 'click here to add your first one',
    '中文名称': 'Chinese Name',
    '日文名称': 'Japanese Name',
    '英文名称': 'English Name',
    '请选择': 'Please Select',
    '机体编号': 'Model Number',
    '所属系列': 'Series',
    '价格信息': 'Price Information',
    '日本价格（日元）': 'Japan Price (JPY)',
    '美国价格（美元）': 'US Price (USD)',
    '中国价格（人民币）': 'China Price (CNY)',
    '定价 (MSRP)': 'MSRP',
    '市场价格': 'Market Price',
    '日元': 'JPY',
    '美元': 'USD',
    '人民币': 'CNY',
    '取消': 'Cancel',
    '保存': 'Save',
    '地区': 'Region',
    '日本': 'Japan',
    '美国': 'US',
    '中国': 'China',
    '算数计算': 'Rate Calculation',
    '基于日本定价': 'Based on Japan MSRP',
    '和': 'and',
    '元': 'CNY',
    '汇率：1人民币 =': 'Exchange rate: 1 CNY =',
    '添加到想要列表': 'Add to Wishlist',
    '已在想要列表': 'Already in Wishlist',
    '添加到已购买': 'Add to Collection',
    '已在已购买列表': 'Already in Collection',
    '导出CSV': 'Export CSV',
    '导入CSV': 'Import CSV',
    '分享清单': 'Shared List',
    '刷新链接': 'Refresh Link',
    '撤销链接': 'Revoke Link',
    '还没有分享链接。': 'No share link yet.',
    '生成分享链接': 'Generate Share Link',
    '添加时间': 'Added Time',
    '确定要移除吗？': 'Are you sure you want to remove it?',
    '移除': 'Remove',
    '列表为空': 'List is Empty',
    '您的想要列表还是空的，': 'Your wishlist is still empty, ',
    '浏览高达列表': 'browse the Gunpla list',
    '并添加到想要列表': ' and add items to wishlist',
    '已购买列表': 'Collection List',
    '购买价格': 'Purchase Price',
    '购买平台': 'Purchase Platform',
    '购买日期': 'Purchase Date',
    '您还没有购买任何高达，': 'You have not purchased any Gunpla yet, ',
    '分享者：': 'Shared by: ',
    '类型：': 'Type: ',
    '此分享清单暂时没有内容。': 'This shared list is empty for now.',
    '添加优惠券': 'Add Coupon',
    '平台': 'Platform',
    '折扣类型': 'Discount Type',
    '折扣值': 'Discount Value',
    '最高减免': 'Max Discount',
    '有效期': 'Validity',
    '状态': 'Status',
    '百分比': 'Percentage',
    '固定金额': 'Fixed Amount',
    '至': 'to',
    '有效': 'Valid',
    '无效': 'Invalid',
    '分析': 'Analyze',
    '暂无优惠券': 'No Coupons',
    '还没有添加任何优惠券，': 'No coupons added yet, ',
    '百分比折扣': 'Percentage Discount',
    '固定金额折扣': 'Fixed Amount Discount',
    '如：8 或 50': 'e.g. 8 or 50',
    '百分比折扣请输入百分比数字（如8表示8折），固定金额请输入金额（如50表示减50元）': 'For percentage, enter a discount number (e.g. 8 means 20% off). For fixed amount, enter value (e.g. 50 means minus 50 CNY).',
    '最高减免金额': 'Maximum Discount Amount',
    '如：50': 'e.g. 50',
    '例如：8折但最高减50元': 'Example: 20% off, capped at 50 CNY.',
    '最低购买金额': 'Minimum Purchase Amount',
    '如：100': 'e.g. 100',
    '有效期开始': 'Valid From',
    '有效期结束': 'Valid Until',
    '描述': 'Description',
    '优惠券描述...': 'Coupon description...',
    '如：8 表示8折': 'e.g. 8 means 20% off',
    '如：50 表示减50元': 'e.g. 50 means minus 50 CNY',
    '优惠券分析': 'Coupon Analysis',
    '优惠券信息': 'Coupon Information',
    '最低购买': 'Minimum Purchase',
    '想要列表中的高达分析（按节省金额排序）': 'Wishlist Gunpla Analysis (sorted by savings)',
    '排名': 'Rank',
    '高达名称': 'Gunpla Name',
    '原价': 'Original Price',
    '优惠后价格': 'Discounted Price',
    '节省金额': 'Savings',
    '折扣率': 'Discount Rate',
    '查看详情': 'View Details',
    '暂无分析数据': 'No Analysis Data',
    '想要列表中没有有价格信息的高达，或者优惠券不适用。': 'No wishlist items with price data, or this coupon is not applicable.',
    '查看想要列表': 'View Wishlist',
    '返回优惠券列表': 'Back to Coupons',
    # Shared feedback
    '请先登录以访问此页面。': 'Please log in to access this page.',
    '用户名至少需要3个字符': 'Username must be at least 3 characters.',
    '密码至少需要6个字符': 'Password must be at least 6 characters.',
    '两次输入的密码不一致': 'Passwords do not match.',
    '用户名已存在': 'Username already exists.',
    '邮箱已被注册': 'Email already registered.',
    '注册成功！请登录': 'Registration successful! Please log in.',
    '请输入用户名和密码': 'Please enter username and password.',
    '用户名或密码错误': 'Invalid username or password.',
    '已成功登出': 'Logged out successfully.',
    '高达添加成功！': 'Gunpla added successfully!',
    '已添加到想要列表！': 'Added to wishlist!',
    '已经在想要列表中了！': 'Already in wishlist!',
    '已从想要列表移除！': 'Removed from wishlist!',
    '无权删除此项目': 'You do not have permission to delete this item.',
    '已添加到已购买列表！': 'Added to collection!',
    '已经在已购买列表中了！': 'Already in collection!',
    '已从已购买列表移除！': 'Removed from collection!',
    '无效的导出类型': 'Invalid export type.',
    '无效的导入类型': 'Invalid import type.',
    '请选择要导入的CSV文件': 'Please choose a CSV file to import.',
    '无效的分享类型': 'Invalid share type.',
    '分享链接已生成': 'Share link created.',
    '分享链接已撤销': 'Share link revoked.',
    '优惠券添加成功！': 'Coupon added successfully!',
}


def get_current_language():
    lang = session.get('lang', 'zh')
    return lang if lang in SUPPORTED_LANGUAGES else 'zh'


def t(text):
    """Translate user-facing text based on current language."""
    if get_current_language() == 'zh':
        return text

    if text in TRANSLATIONS_EN:
        return TRANSLATIONS_EN[text]

    if text.startswith('欢迎回来，') and text.endswith('！'):
        username = text[len('欢迎回来，'):-1]
        return f'Welcome back, {username}!'

    if text.startswith('注册失败：'):
        detail = text.split('：', 1)[1]
        return f'Registration failed: {detail}'

    if text.startswith('添加失败：'):
        detail = text.split('：', 1)[1]
        return f'Add failed: {detail}'

    if text.startswith('导入失败：'):
        detail = text.split('：', 1)[1]
        return f'Import failed: {detail}'

    if text.startswith('导入完成：'):
        detail = text.split('：', 1)[1]
        return f'Import completed: {detail}'

    return text


def _is_safe_redirect_url(target):
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.context_processor
def inject_i18n_helpers():
    return {'t': t, 'current_lang': get_current_language()}


@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in SUPPORTED_LANGUAGES:
        session['lang'] = lang
    else:
        session['lang'] = 'zh'

    next_url = request.args.get('next') or request.referrer
    if not _is_safe_redirect_url(next_url):
        next_url = url_for('index')
    return redirect(next_url)

@login_manager.user_loader
def load_user(user_id):
    """加载用户"""
    return User.query.get(int(user_id))

# 在应用上下文中创建所有表
with app.app_context():
    db.create_all()
    # Seed initial Gunpla data from CSV if database is empty
    if Gunpla.query.first() is None:
        seed_path = os.path.join(os.path.dirname(__file__), "data", "seed_gunpla.csv")
        if os.path.exists(seed_path):
            try:
                with open(seed_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = []
                    for row in reader:
                        cleaned = {}
                        for key, value in row.items():
                            if value is None or value == "":
                                cleaned[key] = None
                                continue
                            if key in {
                                "id",
                            }:
                                cleaned[key] = int(value)
                            elif key in {
                                "price_jp_msrp",
                                "price_jp_market",
                                "price_us_msrp",
                                "price_us_market",
                                "price_cn_msrp",
                                "price_cn_market",
                            }:
                                cleaned[key] = float(value)
                            else:
                                cleaned[key] = value
                        rows.append(cleaned)
                if rows:
                    db.session.bulk_insert_mappings(Gunpla, rows)
                    db.session.commit()
                    print(f"Seeded Gunpla rows: {len(rows)}")
            except Exception as e:
                db.session.rollback()
                print(f"Seed failed: {e}")


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


def _safe_parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), '%Y-%m-%d').date()
    except ValueError:
        return None


def _get_user_list_items(list_type, user_id):
    if list_type == 'wishlist':
        return Wishlist.query.filter_by(user_id=user_id).order_by(Wishlist.added_at.desc()).all()
    if list_type == 'collection':
        return Collection.query.filter_by(user_id=user_id).order_by(Collection.purchase_date.desc()).all()
    return []


@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # 验证输入
        if not username or len(username) < 3:
            flash('用户名至少需要3个字符', 'error')
            return render_template('register.html')
        
        if not password or len(password) < 6:
            flash('密码至少需要6个字符', 'error')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('两次输入的密码不一致', 'error')
            return render_template('register.html')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('register.html')
        
        # 检查邮箱是否已存在（如果提供了邮箱）
        if email and User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'error')
            return render_template('register.html')
        
        # 创建新用户
        try:
            user = User(username=username, email=email if email else None)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('注册成功！请登录', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'注册失败：{str(e)}', 'error')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('已成功登出', 'success')
    return redirect(url_for('index'))


@app.route('/api/subcategories')
def api_subcategories():
    """API: 获取子分类列表"""
    grade = request.args.get('grade', '')
    
    if grade:
        # 获取指定级别的子分类
        subcategories = db.session.query(Gunpla.subcategory).filter(
            Gunpla.grade == grade,
            Gunpla.subcategory.isnot(None),
            Gunpla.subcategory != ''
        ).distinct().all()
    else:
        # 获取所有子分类
        subcategories = db.session.query(Gunpla.subcategory).filter(
            Gunpla.subcategory.isnot(None),
            Gunpla.subcategory != ''
        ).distinct().all()
    
    subcategories = [s[0] for s in subcategories if s[0]]
    
    # 排序子分类
    subcategory_order = ['普通版', '网络限定版', '其他限定版', 'EVANGELION系列', '勇者王系列', 
                        '参考出品/开发中', 'Unleashed', '定制部件', '综合系列',
                        'EXtreme', '限定电镀版', '限量版RX-79[G]特别涂装版', '竞赛奖品版',
                        '水晶版', '彩色电镀版', '圣战士丹拜因', '机动警察', '一年战争版',
                        '往期未商品化参考出品', '特别版', 'HG 40周年纪念系列 (非HGUC)',
                        'HG 30周年纪念版 (非HGUC)', 'HG U.C.Hard Graph', 'HG(1990)系列 (非HGUC)',
                        '往期未商品化/开发中 企划&参考出品', '1/144系列', 'HG创战元宇宙', 'EG GBM',
                        'SDCS GBM', 'FRS GBM', 'HG高达破坏者 对战记录', 'HG高达创形者',
                        'HG高达创战者', 'HG高达创战者TRY', 'HG高达创形者Re:RISE',
                        'HG Customize Campaign', 'HG PETIT\'GGUY', 'HG PETIT\'GGUY 其他限定版', 'HAROPLA',
                        '装甲核心', 'Porta Nova', 'Porta Nova 拓展配件', 'Cielnova', 'Cielnova 拓展配件',
                        'Spinatio', 'Spinatio 扩展配件', '水贴', '30MM 自定义材质', '30MM 自定义场景',
                        '30MM 自定义特效', '特殊限定版', '1/144 泰克普罗托',
                        '超级机器人系列', '拓展部件', '未商品化往期参考出品']
    subcategories_sorted = []
    for sc in subcategory_order:
        if sc in subcategories:
            subcategories_sorted.append(sc)
    for sc in subcategories:
        if sc not in subcategories_sorted:
            subcategories_sorted.append(sc)
    
    return jsonify({'subcategories': subcategories_sorted})


@app.route('/gunpla')
def gunpla_list():
    """高达列表页面"""
    # 获取查询参数
    search = request.args.get('search', '')
    grade = request.args.get('grade', '')
    subcategory = request.args.get('subcategory', '')
    
    # 构建查询
    query = Gunpla.query
    
    if search:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Gunpla.name_cn.contains(search),
                Gunpla.name_jp.contains(search),
                Gunpla.name_en.contains(search),
                Gunpla.ms_number.contains(search)
            )
        )
    
    if grade:
        query = query.filter(Gunpla.grade == grade)
    
    if subcategory:
        query = query.filter(Gunpla.subcategory == subcategory)
    
    gunpla_list = query.order_by(Gunpla.name_cn).all()
    
    # 获取所有级别用于筛选
    grades = db.session.query(Gunpla.grade).distinct().all()
    grades = [g[0] for g in grades if g[0]]
    
    # 获取所有子分类用于筛选
    # 如果选择了级别，只显示该级别的子分类；否则显示所有子分类
    if grade:
        subcategories = db.session.query(Gunpla.subcategory).filter(
            Gunpla.grade == grade,
            Gunpla.subcategory.isnot(None),
            Gunpla.subcategory != ''
        ).distinct().all()
        subcategories = [s[0] for s in subcategories if s[0]]
    else:
        # 没有选择级别时，显示所有子分类
        subcategories = db.session.query(Gunpla.subcategory).filter(
            Gunpla.subcategory.isnot(None),
            Gunpla.subcategory != ''
        ).distinct().all()
        subcategories = [s[0] for s in subcategories if s[0]]
    
    # 排序子分类，让"普通版"排在前面
    subcategory_order = ['普通版', '网络限定版', '其他限定版', 'EVANGELION系列', '勇者王系列', 
                        '参考出品/开发中', 'Unleashed', '定制部件', '综合系列',
                        'EXtreme', '限定电镀版', '限量版RX-79[G]特别涂装版', '竞赛奖品版',
                        '水晶版', '彩色电镀版', '圣战士丹拜因', '机动警察', '一年战争版',
                        '往期未商品化参考出品', '特别版', 'HG 40周年纪念系列 (非HGUC)',
                        'HG 30周年纪念版 (非HGUC)', 'HG U.C.Hard Graph', 'HG(1990)系列 (非HGUC)',
                        '往期未商品化/开发中 企划&参考出品', '1/144系列', 'HG创战元宇宙', 'EG GBM',
                        'SDCS GBM', 'FRS GBM', 'HG高达破坏者 对战记录', 'HG高达创形者',
                        'HG高达创战者', 'HG高达创战者TRY', 'HG高达创形者Re:RISE',
                        'HG Customize Campaign', 'HG PETIT\'GGUY', 'HG PETIT\'GGUY 其他限定版', 'HAROPLA',
                        '装甲核心', 'Porta Nova', 'Porta Nova 拓展配件', 'Cielnova', 'Cielnova 拓展配件',
                        'Spinatio', 'Spinatio 扩展配件', '水贴', '30MM 自定义材质', '30MM 自定义场景',
                        '30MM 自定义特效', '特殊限定版', '1/144 泰克普罗托',
                        '超级机器人系列', '拓展部件', '未商品化往期参考出品']
    subcategories_sorted = []
    for sc in subcategory_order:
        if sc in subcategories:
            subcategories_sorted.append(sc)
    # 添加其他未在排序列表中的子分类
    for sc in subcategories:
        if sc not in subcategories_sorted:
            subcategories_sorted.append(sc)
    subcategories = subcategories_sorted
    
    return render_template('gunpla_list.html', 
                         gunpla_list=gunpla_list,
                         grades=grades,
                         subcategories=subcategories,
                         search=search,
                         selected_grade=grade,
                         selected_subcategory=subcategory)


@app.route('/gunpla/add', methods=['GET', 'POST'])
def gunpla_add():
    """添加高达"""
    if request.method == 'POST':
        try:
            gunpla = Gunpla(
                name_cn=request.form.get('name_cn'),
                name_jp=request.form.get('name_jp') or None,
                name_en=request.form.get('name_en') or None,
                grade=request.form.get('grade'),
                ms_number=request.form.get('ms_number') or None,
                series=request.form.get('series') or None,
                price_jp_msrp=float(request.form.get('price_jp_msrp')) if request.form.get('price_jp_msrp') else None,
                price_jp_market=float(request.form.get('price_jp_market')) if request.form.get('price_jp_market') else None,
                price_us_msrp=float(request.form.get('price_us_msrp')) if request.form.get('price_us_msrp') else None,
                price_us_market=float(request.form.get('price_us_market')) if request.form.get('price_us_market') else None,
                price_cn_msrp=float(request.form.get('price_cn_msrp')) if request.form.get('price_cn_msrp') else None,
                price_cn_market=float(request.form.get('price_cn_market')) if request.form.get('price_cn_market') else None,
            )
            db.session.add(gunpla)
            db.session.commit()
            flash('高达添加成功！', 'success')
            return redirect(url_for('gunpla_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    grades = ['MG', 'RG', 'HGUC', 'HGGTO', 'HGBF/BD', 'HGIBO', 'EG', 'PG', 'SD', 'SDCS', '30MM', 'FM', '成品', '国产盗版', '其他']
    return render_template('gunpla_add.html', grades=grades)


@app.route('/gunpla/<int:gunpla_id>')
def gunpla_detail(gunpla_id):
    """高达详情页面"""
    gunpla = Gunpla.query.get_or_404(gunpla_id)
    
    # 检查是否在想要列表或已购买列表
    in_wishlist = Wishlist.query.filter_by(gunpla_id=gunpla_id).first() is not None
    in_collection = Collection.query.filter_by(gunpla_id=gunpla_id).first() is not None
    
    return render_template('gunpla_detail.html', 
                         gunpla=gunpla,
                         in_wishlist=in_wishlist,
                         in_collection=in_collection,
                         jpy_rate=app.config['JPY_TO_CNY_RATE'])


@app.route('/wishlist')
def wishlist():
    """想要列表"""
    # 如果用户已登录，只显示该用户的列表；否则显示所有公共列表
    if current_user.is_authenticated:
        items = Wishlist.query.filter(
            (Wishlist.user_id == current_user.id) | (Wishlist.user_id.is_(None))
        ).order_by(Wishlist.added_at.desc()).all()
    else:
        items = Wishlist.query.filter_by(user_id=None).order_by(Wishlist.added_at.desc()).all()
    share_link = None
    if current_user.is_authenticated:
        share_link = ShareLink.query.filter_by(
            user_id=current_user.id,
            list_type='wishlist',
            is_active=True
        ).first()
    return render_template('wishlist.html', items=items, share_link=share_link)


@app.route('/collection')
def collection():
    """已购买列表"""
    # 如果用户已登录，只显示该用户的列表；否则显示所有公共列表
    if current_user.is_authenticated:
        items = Collection.query.filter(
            (Collection.user_id == current_user.id) | (Collection.user_id.is_(None))
        ).order_by(Collection.purchase_date.desc()).all()
    else:
        items = Collection.query.filter_by(user_id=None).order_by(Collection.purchase_date.desc()).all()
    share_link = None
    if current_user.is_authenticated:
        share_link = ShareLink.query.filter_by(
            user_id=current_user.id,
            list_type='collection',
            is_active=True
        ).first()
    return render_template('collection.html', items=items, share_link=share_link)


@app.route('/wishlist/add', methods=['POST'])
def wishlist_add():
    """添加到想要列表"""
    gunpla_id = request.form.get('gunpla_id')
    if gunpla_id:
        # 检查是否已存在（根据用户）
        if current_user.is_authenticated:
            existing = Wishlist.query.filter_by(
                gunpla_id=gunpla_id,
                user_id=current_user.id
            ).first()
            if not existing:
                wishlist_item = Wishlist(gunpla_id=gunpla_id, user_id=current_user.id)
                db.session.add(wishlist_item)
                db.session.commit()
                flash('已添加到想要列表！', 'success')
            else:
                flash('已经在想要列表中了！', 'info')
        else:
            # 未登录用户使用公共列表
            existing = Wishlist.query.filter_by(
                gunpla_id=gunpla_id,
                user_id=None
            ).first()
            if not existing:
                wishlist_item = Wishlist(gunpla_id=gunpla_id, user_id=None)
                db.session.add(wishlist_item)
                db.session.commit()
                flash('已添加到想要列表！', 'success')
            else:
                flash('已经在想要列表中了！', 'info')
    return redirect(request.referrer or url_for('gunpla_list'))


@app.route('/wishlist/remove', methods=['POST'])
def wishlist_remove():
    """从想要列表移除"""
    item_id = request.form.get('item_id')
    if item_id:
        item = Wishlist.query.get(item_id)
        if item:
            # 检查权限：只有所有者或未登录用户操作公共列表
            if current_user.is_authenticated:
                if item.user_id == current_user.id:
                    db.session.delete(item)
                    db.session.commit()
                    flash('已从想要列表移除！', 'success')
                else:
                    flash('无权删除此项目', 'error')
            else:
                if item.user_id is None:
                    db.session.delete(item)
                    db.session.commit()
                    flash('已从想要列表移除！', 'success')
                else:
                    flash('无权删除此项目', 'error')
    return redirect(url_for('wishlist'))


@app.route('/collection/add', methods=['POST'])
def collection_add():
    """添加到已购买列表"""
    gunpla_id = request.form.get('gunpla_id')
    if gunpla_id:
        # 检查是否已存在（根据用户）
        if current_user.is_authenticated:
            existing = Collection.query.filter_by(
                gunpla_id=gunpla_id,
                user_id=current_user.id
            ).first()
            if not existing:
                collection_item = Collection(gunpla_id=gunpla_id, user_id=current_user.id)
                db.session.add(collection_item)
                db.session.commit()
                flash('已添加到已购买列表！', 'success')
            else:
                flash('已经在已购买列表中了！', 'info')
        else:
            # 未登录用户使用公共列表
            existing = Collection.query.filter_by(
                gunpla_id=gunpla_id,
                user_id=None
            ).first()
            if not existing:
                collection_item = Collection(gunpla_id=gunpla_id, user_id=None)
                db.session.add(collection_item)
                db.session.commit()
                flash('已添加到已购买列表！', 'success')
            else:
                flash('已经在已购买列表中了！', 'info')
    return redirect(request.referrer or url_for('gunpla_list'))


@app.route('/collection/remove', methods=['POST'])
def collection_remove():
    """从已购买列表移除"""
    item_id = request.form.get('item_id')
    if item_id:
        item = Collection.query.get(item_id)
        if item:
            # 检查权限：只有所有者或未登录用户操作公共列表
            if current_user.is_authenticated:
                if item.user_id == current_user.id:
                    db.session.delete(item)
                    db.session.commit()
                    flash('已从已购买列表移除！', 'success')
                else:
                    flash('无权删除此项目', 'error')
            else:
                if item.user_id is None:
                    db.session.delete(item)
                    db.session.commit()
                    flash('已从已购买列表移除！', 'success')
                else:
                    flash('无权删除此项目', 'error')
    return redirect(url_for('collection'))


@app.route('/export/<list_type>')
@login_required
def export_list(list_type):
    """导出想要/已购买列表为CSV"""
    if list_type not in ['wishlist', 'collection']:
        flash('无效的导出类型', 'error')
        return redirect(url_for('index'))

    items = _get_user_list_items(list_type, current_user.id)

    output = io.StringIO()
    writer = csv.writer(output)

    if list_type == 'wishlist':
        writer.writerow([
            'name_cn', 'grade', 'subcategory', 'price_jp_msrp', 'price_us_msrp', 'price_cn_msrp',
            'notes', 'added_at'
        ])
        for item in items:
            writer.writerow([
                item.gunpla.name_cn if item.gunpla else '',
                item.gunpla.grade if item.gunpla else '',
                item.gunpla.subcategory if item.gunpla else '',
                item.gunpla.price_jp_msrp if item.gunpla else '',
                item.gunpla.price_us_msrp if item.gunpla else '',
                item.gunpla.price_cn_msrp if item.gunpla else '',
                item.notes or '',
                item.added_at.strftime('%Y-%m-%d') if item.added_at else ''
            ])
    else:
        writer.writerow([
            'name_cn', 'grade', 'subcategory', 'purchase_price', 'purchase_platform',
            'purchase_date', 'notes'
        ])
        for item in items:
            writer.writerow([
                item.gunpla.name_cn if item.gunpla else '',
                item.gunpla.grade if item.gunpla else '',
                item.gunpla.subcategory if item.gunpla else '',
                item.purchase_price if item.purchase_price is not None else '',
                item.purchase_platform or '',
                item.purchase_date.strftime('%Y-%m-%d') if item.purchase_date else '',
                item.notes or ''
            ])

    filename = f'{list_type}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    return response


@app.route('/import/<list_type>', methods=['POST'])
@login_required
def import_list(list_type):
    """从CSV导入想要/已购买列表"""
    if list_type not in ['wishlist', 'collection']:
        flash('无效的导入类型', 'error')
        return redirect(url_for('index'))

    file = request.files.get('file')
    if not file or file.filename == '':
        flash('请选择要导入的CSV文件', 'error')
        return redirect(url_for('wishlist' if list_type == 'wishlist' else 'collection'))

    try:
        content = file.stream.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(content))

        added = 0
        skipped = 0
        not_found = 0

        for row in reader:
            name_cn = (row.get('name_cn') or row.get('name') or row.get('名称') or '').strip()
            grade = (row.get('grade') or row.get('级别') or '').strip()

            if not name_cn:
                skipped += 1
                continue

            query = Gunpla.query.filter_by(name_cn=name_cn)
            if grade:
                query = query.filter_by(grade=grade)
            gunpla = query.first()

            if not gunpla:
                not_found += 1
                continue

            if list_type == 'wishlist':
                existing = Wishlist.query.filter_by(
                    gunpla_id=gunpla.id,
                    user_id=current_user.id
                ).first()
                if existing:
                    skipped += 1
                    continue
                wishlist_item = Wishlist(
                    gunpla_id=gunpla.id,
                    user_id=current_user.id,
                    notes=(row.get('notes') or row.get('备注') or None)
                )
                db.session.add(wishlist_item)
                added += 1
            else:
                existing = Collection.query.filter_by(
                    gunpla_id=gunpla.id,
                    user_id=current_user.id
                ).first()
                if existing:
                    skipped += 1
                    continue
                purchase_price = row.get('purchase_price') or row.get('购买价格')
                collection_item = Collection(
                    gunpla_id=gunpla.id,
                    user_id=current_user.id,
                    purchase_price=float(purchase_price) if purchase_price else None,
                    purchase_platform=(row.get('purchase_platform') or row.get('购买平台') or None),
                    purchase_date=_safe_parse_date(row.get('purchase_date') or row.get('购买日期')),
                    notes=(row.get('notes') or row.get('备注') or None)
                )
                db.session.add(collection_item)
                added += 1

        db.session.commit()
        flash(f'导入完成：新增 {added} 条，跳过 {skipped} 条，未匹配 {not_found} 条', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'导入失败：{str(e)}', 'error')

    return redirect(url_for('wishlist' if list_type == 'wishlist' else 'collection'))


@app.route('/share/create/<list_type>', methods=['POST'])
@login_required
def share_create(list_type):
    """创建分享链接"""
    if list_type not in ['wishlist', 'collection']:
        flash('无效的分享类型', 'error')
        return redirect(url_for('index'))

    existing_links = ShareLink.query.filter_by(
        user_id=current_user.id,
        list_type=list_type,
        is_active=True
    ).all()
    for link in existing_links:
        link.is_active = False

    token = secrets.token_urlsafe(16)
    share_link = ShareLink(
        user_id=current_user.id,
        list_type=list_type,
        token=token,
        is_active=True
    )
    db.session.add(share_link)
    db.session.commit()

    flash('分享链接已生成', 'success')
    return redirect(url_for('wishlist' if list_type == 'wishlist' else 'collection'))


@app.route('/share/revoke/<list_type>', methods=['POST'])
@login_required
def share_revoke(list_type):
    """撤销分享链接"""
    if list_type not in ['wishlist', 'collection']:
        flash('无效的分享类型', 'error')
        return redirect(url_for('index'))

    existing_links = ShareLink.query.filter_by(
        user_id=current_user.id,
        list_type=list_type,
        is_active=True
    ).all()
    for link in existing_links:
        link.is_active = False

    db.session.commit()
    flash('分享链接已撤销', 'success')
    return redirect(url_for('wishlist' if list_type == 'wishlist' else 'collection'))


@app.route('/share/<token>')
def share_view(token):
    """查看分享列表"""
    share_link = ShareLink.query.filter_by(token=token, is_active=True).first_or_404()
    items = _get_user_list_items(share_link.list_type, share_link.user_id)
    owner = User.query.get(share_link.user_id)
    return render_template('share_list.html', share_link=share_link, items=items, owner=owner)


@app.route('/coupons')
def coupons():
    """优惠券列表"""
    coupon_list = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return render_template('coupons.html', coupons=coupon_list)


@app.route('/coupons/add', methods=['GET', 'POST'])
def coupon_add():
    """添加优惠券"""
    if request.method == 'POST':
        try:
            valid_from = None
            valid_until = None
            if request.form.get('valid_from'):
                valid_from = datetime.strptime(request.form.get('valid_from'), '%Y-%m-%d').date()
            if request.form.get('valid_until'):
                valid_until = datetime.strptime(request.form.get('valid_until'), '%Y-%m-%d').date()
            
            coupon = Coupon(
                platform=request.form.get('platform'),
                discount_type=request.form.get('discount_type'),
                discount_value=float(request.form.get('discount_value')),
                max_discount=float(request.form.get('max_discount')) if request.form.get('max_discount') else None,
                min_purchase=float(request.form.get('min_purchase')) if request.form.get('min_purchase') else None,
                valid_from=valid_from,
                valid_until=valid_until,
                description=request.form.get('description') or None
            )
            db.session.add(coupon)
            db.session.commit()
            flash('优惠券添加成功！', 'success')
            return redirect(url_for('coupons'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败：{str(e)}', 'error')
    
    platforms = ['淘宝', '拼多多', '京东', '其他']
    return render_template('coupon_add.html', platforms=platforms)


@app.route('/coupons/<int:coupon_id>/analyze')
def coupon_analyze(coupon_id):
    """优惠券分析"""
    coupon = Coupon.query.get_or_404(coupon_id)
    wishlist_items = Wishlist.query.all()
    
    # 分析每个想要列表中的高达
    analyses = []
    for item in wishlist_items:
        gunpla = item.gunpla
        if gunpla.price_cn_market:
            analysis = coupon.calculate_discount(gunpla.price_cn_market)
            analyses.append({
                'gunpla': gunpla,
                'analysis': analysis,
                'original_price': gunpla.price_cn_market
            })
    
    # 按节省金额排序
    analyses.sort(key=lambda x: x['analysis']['savings'], reverse=True)
    
    return render_template('coupon_analyze.html', coupon=coupon, analyses=analyses)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(debug=debug, host='0.0.0.0', port=port)

