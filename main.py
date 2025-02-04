# 从 Flask 库中导入所需的模块和函数
# Flask 用于创建 Flask 应用实例
# redirect 用于重定向到指定的 URL
# url_for 用于根据视图函数名生成对应的 URL
# render_template 用于渲染 HTML 模板
# session 用于管理用户会话
from flask import Flask, redirect, url_for, render_template, session
# 从自定义的安全配置模块中导入配置安全相关的函数
from config.security import configure_security
# 从自定义的数据加载工具模块中导入加载数据的函数
from utils.data_loader import load_data
# 从自定义的路由工具模块中导入注册步骤路由的函数
from utils.routing import register_steps
# 从 datetime 模块中导入 timedelta 类，用于设置会话超时时间
from datetime import timedelta
# 从自定义的管理模块中导入管理蓝图和初始化管理界面的函数
from admin import admin_bp, init_admin

# 创建一个 Flask 应用实例
app = Flask(__name__)

# 设置会话密钥，用于加密会话数据
# 建议使用更复杂、安全的密钥，这里只是示例
app.secret_key = 'your_secret_key_here'  

# 全局禁用 CSRF 保护
# CSRF（跨站请求伪造）保护是 Flask-WTF 提供的安全机制，这里选择禁用
app.config['WTF_CSRF_ENABLED'] = False

# 设置会话超时时间，使用 timedelta 类指定为 30 分钟
# 当会话在 30 分钟内没有活动时，会话将过期
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# 调用自定义的安全配置函数，对应用进行安全相关的配置
configure_security(app)

# 调用自定义的数据加载函数，将加载的数据存储到应用实例的 data 属性中
app.data = load_data()
# 打印加载的数据，方便查看数据是否正确加载
print("Loaded data:", app.data)  

# 调用自定义的路由注册函数，动态注册步骤路由
register_steps(app)

# 定义根路径的路由，当用户访问应用的根 URL 时，会触发此视图函数
@app.route('/')
def home():
    # 设置会话为持久化，即会话会在指定的超时时间内保持有效
    session.permanent = True  
    # 打印在清除会话数据之前的会话内容，方便调试
    print("Session data before clearing in home route:", session)
    # 清除会话中的所有数据
    session.clear()
    # 打印在清除会话数据之后的会话内容，方便调试
    print("Session data after clearing in home route:", session)
    # 重定向到名为 'step1' 的视图函数对应的 URL
    return redirect(url_for('step1'))

# 定义结果页面的路由，当用户访问 /result 时，会触发此视图函数
@app.route('/result')
def result():
    # 从会话中获取 product_id
    product_id = session.get('product_id')
    # 如果 product_id 存在，将其转换为小写并去除首尾空格
    if product_id:
        product_id = product_id.strip().lower()  
    # 检查 product_id 是否存在，以及在加载的数据中是否有对应的产品信息
    if not product_id or not app.data['products'].get(product_id):
        # 如果不存在，渲染错误页面，并传递错误信息
        return render_template('error.html', message='会话已过期，请重新开始')

    # 从加载的数据中获取产品的详细信息
    product_data = app.data['products'][product_id]
    new_material_price = session.get('new_material_price')
    # 计算材料成本，根据产品的重量和原材料单价计算
    material_cost = product_data['weight'] * new_material_price / 1000000*100/session.get('plating_return') 
    process_cost = (app.data['process_price'] / product_data['molds_per_unit'])*100/session.get('plating_return') 
    # 根据会话中记录的电镀类型计算电镀成本
    if session['plating_type'] == 'shake':
        # 如果是摇板电镀，根据产品的基础费用和颜色费用计算
        plating_cost = app.data['plating_shake'][product_id]['base_fee'] * app.data['colors'][session['color']]
    elif session['plating_type'] == 'insert':
        # 如果是插起来电镀，根据产品的基础费用和颜色费用计算
        plating_cost = app.data['plating_insert'][product_id]['base_fee'] 
    else:
        # 如果是整板电镀，只根据产品的基础费用计算
        plating_cost = app.data['plating_whole'] / product_data['molds_per_unit']

    # 计算钻石成本，如果需要点钻石，则根据钻石数量和点钻单价计算
    
    if session['need_diamond'] == 'yes':
        diamond_cost = app.data['diamond'] * session.get('diamond_count') 
    else: 
        diamond_cost = 0
    
    # 计算点油成本，如果需要点油，则根据点油费用计算
    if session['need_oil'] == 'yes':
        oil_cost = app.data['oil'][product_id]['price'] 
    else:
        oil_cost = 0

    # 计算手工成本，如果需要手工加工，则根据手工价格计算
    if session['need_handmade'] == 'yes':
        handmade_cost = session.get('handmade_count') 
    else: 
        handmade_cost = 0
    

    # 计算总成本，将材料成本、电镀成本、钻石成本和点油成本相加
    total_cost = material_cost + plating_cost + diamond_cost + oil_cost + process_cost + handmade_cost

    # 渲染结果页面，传递产品 ID、总成本和各项成本的详细信息
    return render_template('result.html',
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
                               'plating_return': (100-session.get('plating_return')),
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

# 调用自定义的初始化管理界面函数，初始化应用的管理界面
init_admin(app)

# 如果当前脚本作为主程序运行，则启动 Flask 应用
if __name__ == '__main__':
    # 指定应用监听的主机地址和端口号
    app.run(host='0.0.0.0', port=8080)