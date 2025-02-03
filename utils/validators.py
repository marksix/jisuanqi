from flask import session, flash
from .data_loader import load_data

def validate_field(validation, form_data):
    field = validation['field']
    value = form_data.get(field, '').strip()
    
    if validation['type'] == 'product_id':
        data = load_data()
        if value.lower() not in data['products']:
            flash('无效的产品编号', 'error')
            return False
    elif validation['type'] == 'color':
        if value not in session.get('available_colors', []):
            flash('无效的颜色选择', 'error')
            return False
    elif validation['type'] == 'drill_count':
        try:
            count = int(value)
            if count < 0:
                raise ValueError
        except ValueError:
            flash('请输入有效的钻石数量', 'error')
            return False
    return True