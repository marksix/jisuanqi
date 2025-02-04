from flask import render_template, request, session, redirect, url_for, flash
import yaml

def register_steps(app):
    with open('config/steps.yaml', encoding='utf-8') as f:
        steps_config = yaml.safe_load(f)['steps']
    for config in steps_config:
        _create_step_handler(app, config)

def _create_step_handler(app, config):
    current_config = config.copy()

    @app.route(current_config['route'], methods=['GET', 'POST'], endpoint=current_config['id'])
    def handler():
        if not _check_requirements(current_config):
            return redirect(url_for('step1'))

        if request.method == 'POST':
            if not _process_form(current_config):
                return _render_template_with_context(app, current_config)
            return _redirect_next(current_config)

        return _render_template_with_context(app, current_config)

    def _check_requirements(config):
        if 'requires' in config:
            try:
                return eval(config['requires'], {'session': session})
            except KeyError:
                return False
        return True

    def _process_form(config):
        for key in request.form:
            value = request.form.get(key).strip()
            if key == 'product_id':
                value = value.lower()  # 将 product_id 转换为小写
            session[key] = value

        if 'validations' in config:
            for validation in config['validations']:
                if not _validate_field(validation):
                    return False
        session.modified = True  # 确保会话数据被保存
        print(f"Session data after processing form for {config['id']}:", session)  # 查看处理表单后的会话数据
        return True

    def _validate_field(validation):
        field = validation['field']
        value = session.get(field, '')

        if validation['type'] == 'product_id':
            if not value or not app.data['products'].get(value.lower()):
                flash('❌ 无效的产品编号', 'error')
                session.modified = True  # 确保会话数据被保存
                return False
        elif validation['type'] == 'number':
            try:
              float(value)
            except ValueError:
                flash('❌ 请输入有效的数字', 'error')
                session.modified = True  # 确保会话数据被保存
                session[field] = value  # 保留用户输入的值
                return False
            session[field] = float(value)
        return True

    def _redirect_next(config):
        print(f"Session data before redirecting from {config['id']}:", session)
        if 'next_logic' in config:
            next_step = eval(config['next_logic'], {'session': session})
        else:
            next_step = config.get('next', 'result')
        return redirect(url_for(next_step))

    def _render_template_with_context(app, config):
        context = _prepare_context(app, config)
        return render_template(config['template'], **context)

def _prepare_context(app, config):
    steps = _get_steps_config()
    current_step_index = next(
        (i for i, step in enumerate(steps) if step['id'] == config['id']),
        0
    ) + 1
    context = {
        'current_step': config,
        'steps': steps,
        'current_step_index': current_step_index,
        'total_steps': len(steps),
        'colors': app.data['colors'].keys() if config['id'] == 'step3' else None,
        'materials': app.data['materials'].keys() if config['id'] == 'step1a' else None
    }

    # 处理 step1b 步骤，获取所选材料的价格
    if config['id'] == 'step1b':
        selected_material_name = session.get('material')
        if selected_material_name:
            selected_material = app.data['materials'].get(selected_material_name)
            context['selected_material'] = selected_material
    return context
    

def _get_steps_config():
    with open('config/steps.yaml', encoding='utf-8') as f:
        return yaml.safe_load(f)['steps']