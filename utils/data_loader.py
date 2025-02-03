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
    # 读取电镀震动数据并处理 product_id
    plating_shake = process_id(pd.read_csv(f'{data_path}/plating_shake.csv'))
    # 读取整体电镀数据并处理 product_id
    plating_whole = process_id(pd.read_csv(f'{data_path}/plating_whole.csv'))
    # 读取颜色价格数据
    colors = pd.read_csv(f'{data_path}/color_prices.csv').set_index('color').to_dict()['price']
    # 读取点钻价格数据
    drill = pd.read_csv(f'{data_path}/drill_price.csv').iloc[0]['price']
    # 读取点油价格数据
    oil = pd.read_csv(f'{data_path}/oil_price.csv').iloc[0]['price']

    return {
        'products': products,
        'plating_shake': plating_shake,
        'plating_whole': plating_whole,
        'colors': colors,
        'drill': drill,
        'oil': oil
    }