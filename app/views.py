# -*- coding: utf-8 -*-

import hashlib
import hmac
import json
import random
import re
import string
import uuid

import requests
from flask import request as req, session, json as f_json, render_template, render_template_string, redirect, \
    url_for, abort

from . import app
from . import event_default_template
from .models import Template
from .models import Token
from .models import db

# https://developer.github.com/webhooks/#events
SUPPORT_EVENTS = [
    'commit_comment',
    'create',
    'delete',
    'deployment',
    'deployment_status',
    'fork',
    'gollum',
    'issue_comment',
    'issues',
    'label',
    'member',
    'milestone',
    'page_build',
    'project_card',
    'project_column',
    'project',
    'public',
    'pull_request_review_comment',
    'pull_request_review',
    'pull_request',
    'push',
    'release',
    'repository',
    'status',
    'team_add',
    'watch'
]


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = \
            ''.join([random.choice(string.ascii_letters + string.digits) for i in range(30)])
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token


@app.before_request
def csrf_protect():
    if req.method == "POST" and not req.path.startswith('/webhook/'):
        csrf_token = session.get('_csrf_token', None)
        if not csrf_token or csrf_token != req.form.get('_csrf_token'):
            abort(403)


@app.route('/webhook/<code>', methods=['POST'])
def handle_webhook(code):
    if not req.is_json:
        return error_json('Use application/json content-type.'), 400

    payload = req.get_json()
    event = req.headers['X-GitHub-Event']

    token = Token.query.filter_by(code=code).first()
    if not token:
        return error_json('Invalid code.'), 400

    if token.secret:
        hub_signature = req.headers.get('X-Hub-Signature', '')
        if not hub_signature:
            return error_json('This code is set secret. So X-Hub-Signature is needed.'), 400
        if not check_signature(req.get_data(), token.secret.encode('utf-8'), hub_signature):
            return error_json('Signature does NOT match.'), 400

    if event == 'ping':
        return f_json.jsonify(message='pong')

    if event not in SUPPORT_EVENTS:
        return f_json.jsonify(message='Not support {} type.'.format(event))

    text = render_message(token, event, payload)
    if not text:
        return f_json.jsonify(message='ignore')

    result = requests.post(
        'https://notify-api.line.me/api/notify',
        data={'message': text}, headers={'Authorization': 'Bearer ' + token.token}
    )
    if result.status_code == 200:
        return f_json.jsonify(message='ok')
    else:
        body = result.json()
        return error_json(body['message']), 400


@app.route('/', methods=['GET'])
def token_list():
    q_token = req.args.get('q_token', '')
    if q_token:
        tokens = Token.query.filter_by(token=q_token).order_by(Token.id.desc()).all()
    else:
        tokens = Token.query.order_by(Token.id.desc()).all()

    return render_template(
        'token_list.html', q_token=q_token, tokens=tokens
    )


@app.route('/token/add', methods=['GET', 'POST'])
def add_token():
    if req.method == 'POST':
        code = str(uuid.uuid4())

        token_dict = {field: req.form[field] for field in ['token', 'secret', 'description']}
        token = Token(code=code, **token_dict)
        db.session.add(token)
        db.session.commit()  # to get id

        templates = []
        for event in SUPPORT_EVENTS:
            templates.append(Template(token_id=token.id, event=event, template=req.form['template.' + event]))
        db.session.bulk_save_objects(templates)
        db.session.commit()

        return redirect(url_for('add_token_complete', code=code))
    else:
        return render_template(
            'token_form.html',
            is_new=True, support_events=SUPPORT_EVENTS,
            templates={event: event_default_template.get(event).strip() for event in SUPPORT_EVENTS}
        )


@app.route('/token/add/complete', methods=['GET'])
def add_token_complete():
    token = Token.query.filter_by(code=req.args['code']).first_or_404()

    return render_template(
        'add_token_complete.html', token=token,
        webhook_url='{}webhook/{}'.format(req.host_url, req.args['code'])
    )


@app.route('/token/<code>', methods=['GET', 'POST'])
def edit_token(code):
    token = Token.query.filter_by(code=code).first_or_404()
    templates = Template.query.filter_by(token_id=token.id).all()

    if req.method == 'POST':
        templates_dict = {template.event: template for template in templates}

        token.description = req.form['description']
        if req.form['token_update'] == 'true':
            token.token = req.form['token']
        if req.form['secret_update'] == 'true':
            token.secret = req.form['secret']

        new_templates = []
        for event in SUPPORT_EVENTS:
            template = templates_dict.get(event)
            template_str = req.form['template.' + event]
            if template:
                template.template = template_str
            else:
                new_templates.append(Template(token_id=token.id, event=event, template=template_str))
        db.session.bulk_save_objects(new_templates)

        db.session.commit()
        return redirect(url_for('token_list'))
    else:
        return render_template(
            'token_form.html',
            webhook_url='{}webhook/{}'.format(req.host_url, token.code),
            support_events=SUPPORT_EVENTS, code=token.code, token=token.token,
            secret=token.secret, description=token.description,
            templates={template.event: template.template for template in templates}
        )


@app.route('/token/delete', methods=['POST'])
def delete_token():
    token = Token.query.filter_by(code=req.form['code']).first_or_404()

    Template.query.filter_by(token_id=token.id).delete()
    db.session.delete(token)
    db.session.commit()
    return redirect(url_for('token_list'))


@app.route('/template/playground', methods=['GET'])
def template_playground():
    return render_template('template_playground.html')


@app.route('/api/template/playground', methods=['POST'])
def api_template_playground():
    try:
        payload_json = f_json.loads(req.form['payload'])
    except json.decoder.JSONDecodeError:
        return error_json('Input payload-json as valid json format.'), 400

    result = render_template_string(autoescape_off(req.form['template']), **payload_json).strip()
    return f_json.jsonify(result=result)


def check_signature(payload, secret, hub_signature):
    signature = hmac.new(secret, payload, hashlib.sha1).hexdigest()
    return hmac.compare_digest(hub_signature, 'sha1=' + signature)


def error_json(message):
    return f_json.jsonify(error={'message': message})


@app.template_filter('simplify_branch')
def simplify_branch(s):
    return re.sub('.*/', '', s)


def autoescape_off(text):
    return '{% autoescape false %}' + text + '{% endautoescape %}'


def render_message(token, event, payload):
    template = Template.query.filter_by(token_id=token.id, event=event).first()
    if not template or not template.template.strip():
        return ''

    # this message used for text of LINE. So don't need escape.
    return render_template_string(autoescape_off(template.template), **payload).strip()
