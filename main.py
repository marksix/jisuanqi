from flask import Flask, redirect, url_for, render_template, session
from config.security import configure_security
from utils.data_loader import load_data
from utils.routing import register_steps
from datetime import timedelta
from admin import admin_bp, init_admin

app = Flask(__name__)

# 设置会话密钥
app.secret_key = 'your_secret_key_here'  # 建议使用更复杂、安全的密钥

# 全局禁用 CSRF 保护
app.config['WTF_CSRF_ENABLED'] = False

# 设置会话超时时间，例如 30 分钟
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# 安全配置
configure_security(app)

# 加载数据到应用实例
app.data = load_data()
print("Loaded data:", app.data)  # 查看加载的数据是否正确

# 动态注册步骤路由
register_steps(app)

# 根路径路由
@app.route('/')
def home():
    session.permanent = True  # 在这里设置会话持久化
    print("Session data before clearing in home route:", session)
    session.clear()
    print("Session data after clearing in home route:", session)
    return redirect(url_for('step1'))

# 结果路由
@app.route('/result')
def result():
    product_id = session.get('product_id')
    if product_id:
        product_id = product_id.strip().lower()  # 将 product_id 转换为小写
    if not product_id or not app.data['products'].get(product_id):
        return render_template('error.html', message='会话已过期，请重新开始')

    product_data = app.data['products'][product_id]

    material_cost = product_data['weight'] * product_data['molds_per_unit']

    if session['plating_type'] == 'shake':
        plating_cost = app.data['plating_shake'][product_id]['base_fee'] + app.data['colors'][session['color']]
    else:
        plating_cost = app.data['plating_whole'][product_id]['base_fee']

    drill_cost = int(app.data['drill']) * session.get('drill_count', 0) if session.get('need_drill') else 0
    oil_cost = int(app.data['oil']) if session.get('need_oil') else 0

    total_cost = material_cost + plating_cost + drill_cost + oil_cost

    return render_template('result.html',
                           product_id=product_id,
                           total_cost=total_cost,
                           details={
                               'material': material_cost,
                               'plating': plating_cost,
                               'drill': drill_cost,
                               'oil': oil_cost
                           })

# 初始化管理界面
init_admin(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)