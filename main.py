# 导入必要的模块和函数
from flask import Flask, redirect, url_for, render_template, session
from flask_talisman import Talisman
from config.security import configure_security
from utils.data_loader import load_data
from utils.routing import register_steps
from datetime import timedelta
from admin import admin_bp, init_admin

# 创建 Flask 应用实例
app = Flask(__name__)

# 应用安全相关设置
# 使用 Talisman 扩展强制使用 HTTPS
Talisman(app)
# 设置会话密钥，用于加密会话数据，实际应用中应使用更复杂、安全的密钥
app.secret_key = 'your_secret_key_here'
# 全局禁用 CSRF 保护
app.config['WTF_CSRF_ENABLED'] = False
# 设置会话超时时间为 30 分钟
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# 调用自定义函数进行安全配置
configure_security(app)

# 加载数据并存储到应用实例的 data 属性中
app.data = load_data()
print("Loaded data:", app.data)

# 注册步骤路由
register_steps(app)

# 定义根路径路由
@app.route('/')
def home():
    # 设置会话为持久化
    session.permanent = True
    # 打印清除会话数据前的会话内容，用于调试
    print("Session data before clearing in home route:", session)
    # 清除会话中的所有数据
    session.clear()
    # 打印清除会话数据后的会话内容，用于调试
    print("Session data after clearing in home route:", session)
    # 重定向到名为 'step1' 的视图函数对应的 URL
    return redirect(url_for('step1'))

# 定义结果页面路由
@app.route('/result')
def result():
    # 从会话中获取 product_id
    product_id = session.get('product_id')
    if product_id:
        # 去除 product_id 首尾空格并转换为小写
        product_id = product_id.strip().lower()
    # 检查 product_id 是否存在以及数据中是否有对应产品信息
    if not product_id:
        return render_template('error.html', message='产品ID信息丢失')
    if product_id not in app.data['products']:
        return render_template('error.html', message=f'未找到产品 ID 为 {product_id} 的产品信息，请重新输入')

    # 检查 product_id 是否存在以及数据中是否有对应产品信息
    #if not product_id or not app.data['products'].get(product_id):
    # 若不存在，渲染错误页面并传递错误信息
        #return render_template('error.html', message='会话已过期，请重新开始')

    # 获取产品详细信息
    product_data = app.data['products'][product_id]
    new_material_price = session.get('new_material_price')

    # 计算各项成本
    # 材料成本
    material_cost = product_data['weight'] * new_material_price / 1000000 * 100 / session.get('plating_return')
    # 加工成本
    process_cost = (app.data['process_price'] / product_data['molds_per_unit']) * 100 / session.get('plating_return')

    # 电镀成本
    if session['plating_type'] == 'shake':
        # 摇板电镀成本
        plating_cost = app.data['plating_shake'][product_id]['base_fee'] * app.data['colors'][session['color']]
    elif session['plating_type'] == 'insert':
        # 插起来电镀成本
        plating_cost = app.data['plating_insert'][product_id]['base_fee']
    else:
        # 整板电镀成本
        plating_cost = app.data['plating_whole'] / product_data['molds_per_unit']

    # 钻石成本
    if session['need_diamond'] == 'yes':
        diamond_cost = app.data['diamond'] * session.get('diamond_count')
    else:
        diamond_cost = 0

    # 点油成本
    if session['need_oil'] == 'yes':
        oil_cost = app.data['oil'][product_id]['price']
    else:
        oil_cost = 0

    # 手工成本
    if session['need_handmade'] == 'yes':
        handmade_cost = session.get('handmade_count')
    else:
        handmade_cost = 0

    # 计算总成本
    total_cost = material_cost + plating_cost + diamond_cost + oil_cost + process_cost + handmade_cost

    # 渲染结果页面，传递相关数据
    return render_template(
        'result.html',
        product_id=product_id,
        total_cost=total_cost,
        details={
            'material': material_cost,
            'process': process_cost,
            'plating': plating_cost,
            'diamond': diamond_cost,
            'oil': oil_cost,
            'handmade': handmade_cost
        },
        describe={
            'plating_return': (100 - session.get('plating_return')),
            'material_price': new_material_price,
            'material_name': session['material'],
            'process_price': app.data['process_price'],
            'plating_method': session['plating_type'],
            'plating_color': session.get('color'),
            'diamond_number': session.get('diamond_count'),
            'oil_need': session['need_oil'],
            'products_weigh': app.data['products'][product_id]['weight'],
            'products_molds': app.data['products'][product_id]['molds_per_unit']
        }
    )

# 初始化应用的管理界面
init_admin(app)

# 主程序入口
if __name__ == '__main__':
    # 启动 Flask 应用，监听指定主机地址和端口号
    app.run(host='0.0.0.0', port=8080)