from flask import Blueprint, request, redirect, url_for, render_template_string
from flask_admin import Admin
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.base import expose
from flask_admin.model.base import BaseModelView
from flask_wtf import FlaskForm
from wtforms import StringField
import csv
import os


admin_bp = Blueprint('admin', __name__)

# 创建 Flask-Admin 实例
admin = Admin(name='数据管理', template_mode='bootstrap3')


# 自定义 CSV 文件视图
class CSVModelView(BaseModelView):
    def __init__(self, path, name=None, category=None, endpoint=None, url=None):
        self.path = path
        # 移除 session 参数
        super(CSVModelView, self).__init__(None, name=name, category=category, endpoint=endpoint, url=url)

    def _get_endpoint(self, endpoint):
        # 重写 _get_endpoint 方法，使用文件名作为端点
        if endpoint:
            return endpoint
        file_name = os.path.splitext(os.path.basename(self.path))[0]
        return f'csv_{file_name}'

    def scaffold_list_columns(self):
        # 实现 scaffold_list_columns 方法，读取 CSV 文件的第一行作为列名
        try:
            with open(self.path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                print(f"Read headers: {headers}")
                return headers
        except FileNotFoundError:
            print("File not found while reading headers.")
            return []
        except Exception as e:
            print(f"Error reading CSV headers: {e}")
            return []

    def scaffold_sortable_columns(self):
        # 实现 scaffold_sortable_columns 方法，让所有列都可排序
        columns = self.scaffold_list_columns()
        return {col: col for col in columns}

    def scaffold_form(self):
        # 实现 scaffold_form 方法，根据列名生成表单字段
        columns = self.scaffold_list_columns()
        form_class = type('CSVForm', (FlaskForm,), {})
        for col in columns:
            setattr(form_class, col, StringField(col))
        return form_class

    def get_one(self, id):
        # 简单实现 get_one 方法，根据行索引获取一行数据
        try:
            with open(self.path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                for i, row in enumerate(reader):
                    if i == id:
                        print(f"Found row {id}: {dict(zip(headers, row))}")
                        return dict(zip(headers, row))
        except FileNotFoundError:
            print("File not found while getting row.")
            return None
        except Exception as e:
            print(f"Error getting row {id}: {e}")
            return None

    def get_list(self, page, sort_column, sort_desc, search, filters, page_size=None):
        # 实现 get_list 方法，获取 CSV 文件中的数据列表
        if page_size is None:
            page_size = 20  # 默认每页显示 20 条记录
        start_index = page * page_size
        end_index = start_index + page_size
        data = []
        try:
            with open(self.path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                for i, row in enumerate(reader):
                    if start_index <= i < end_index:
                        data.append(dict(zip(headers, row)))
                    elif i >= end_index:
                        break
            total_count = sum(1 for _ in csv.reader(open(self.path, 'r', newline='', encoding='utf-8'))) - 1
            print(f"Total records: {total_count}, Page {page} data: {data}")
            return total_count, data
        except FileNotFoundError:
            print("File not found while getting data list.")
            return 0, []
        except Exception as e:
            print(f"Error getting data list: {e}")
            return 0, []

    def create_model(self, form):
        # 实现 create_model 方法，向 CSV 文件中添加新行
        new_row = [form.data[col] for col in self.scaffold_list_columns()]
        try:
            with open(self.path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(new_row)
            return True
        except Exception as e:
            # 处理异常
            print(f"Error creating model: {e}")
            return False

    def update_model(self, form, model):
        # 实现 update_model 方法，更新 CSV 文件中的一行数据
        all_data = []
        headers = []
        try:
            with open(self.path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                for i, row in enumerate(reader):
                    if i == model:
                        new_row = [form.data[col] for col in headers]
                        all_data.append(new_row)
                    else:
                        all_data.append(row)
            with open(self.path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(all_data)
            return True
        except Exception as e:
            # 处理异常
            print(f"Error updating model: {e}")
            return False

    def delete_model(self, model):
        # 实现 delete_model 方法，从 CSV 文件中删除一行数据
        all_data = []
        headers = []
        try:
            with open(self.path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                for i, row in enumerate(reader):
                    if i != model:
                        all_data.append(row)
            with open(self.path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(all_data)
            return True
        except Exception as e:
            # 处理异常
            print(f"Error deleting model: {e}")
            return False

    def get_pk_value(self, model):
        # 实现 get_pk_value 方法，返回行索引作为主键值
        try:
            data = []
            with open(self.path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                for row in reader:
                    data.append(dict(zip(headers, row)))
            return data.index(model)
        except ValueError:
            return None
        except Exception as e:
            # 处理异常
            print(f"Error getting primary key value: {e}")
            return None

    @expose('/')
    def index_view(self):
        count, data = self.get_list(page=0, sort_column=None, sort_desc=False, search=None, filters=None)
        headers = self.scaffold_list_columns()
        # 详细打印数据，确认键值对
        for row in data:
            print(f"Row data: {row}")
        print(f"Rendering data: {data}, Headers: {headers}")
        return self.render('admin/csv_index.html', data=data, headers=headers)


# 添加文件管理视图
data_dir = os.path.join(os.path.dirname(__file__), 'data')
admin.add_view(FileAdmin(data_dir, name='数据文件'))

# 为每个 CSV 文件添加自定义视图
for file in os.listdir(data_dir):
    if file.endswith('.csv'):
        file_path = os.path.join(data_dir, file)
        view = CSVModelView(file_path, name=file, category='CSV 数据')
        admin.add_view(view)


def init_admin(app):
    admin.init_app(app)