import pandas as pd
import os

def load_data():
    data_path = os.path.join(os.path.dirname(__file__), '../data')

    def process_id(df):
        if 'product_id' in df.columns:
            # 去除前后空格并转换为小写
            df['product_id'] = df['product_id'].str.strip().str.lower()
        return df.set_index('product_id').to_dict('index')

    # 读取产品数据并处理 product_id
    products = process_id(pd.read_csv(f'{data_path}/products.csv'))
    # 读取摇镀数据并处理 product_id
    plating_shake = process_id(pd.read_csv(f'{data_path}/plating_shake.csv'))
    # 读取颜色价格数据
    colors = pd.read_csv(f'{data_path}/color_prices.csv').set_index('color').to_dict()['price']
     # 读取插镀价格数据并处理 product_id
    plating_insert = process_id(pd.read_csv(f'{data_path}/plating_insert.csv'))
    # 读取板镀价格数据并处理 product_id
    plating_whole = float(pd.read_csv(f'{data_path}/plating_whole.csv').iloc[0]['price'])
    # 读取点钻价格数据
    diamond = float(pd.read_csv(f'{data_path}/diamond_price.csv').iloc[0]['price'])
    # 读取注塑加工价格数据
    process_price = float(pd.read_csv(f'{data_path}/process_prices.csv').iloc[0]['price'])
    # 读取点油价格数据
    oil = process_id(pd.read_csv(f'{data_path}/oil_price.csv'))
    # 读取材料价格数据
    materials = pd.read_csv(f'{data_path}/material_prices.csv').set_index('material').to_dict()['price']

    return {
        'products': products,
        'plating_shake': plating_shake,
        'plating_whole': plating_whole,
        'plating_insert': plating_insert,
        'colors': colors,
        'diamond': diamond,
        'oil': oil,
        'materials': materials,
        'process_price': process_price
    }