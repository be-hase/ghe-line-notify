# -*- coding: utf-8 -*-

__commit_comment = '''
{{ sender.login }} {{ action }} comment on commit {{ repository.full_name }}@{{ comment.commit_id|truncate(7, True, '') }}

{{ comment.body|trim|truncate }}

{{ comment.html_url }}
'''

__create = '''
{{ sender.login }} created {{ ref_type }} {{ ref }} at {{ repository.full_name}}

{{ repository.html_url }}
'''

__delete = '''
{{ sender.login }} deleted {{ ref_type }} {{ ref }} at {{ repository.full_name}}

{{ repository.html_url }}
'''

__issue_comment = '''
{{ sender.login }} {{ action }} comment on issue {{ repository.full_name }}#{{ issue.number }}

{{ comment.body|trim|truncate }}

{{ comment.html_url }}
'''

__issues = '''
{{ sender.login }} {{ action }} issue {{ repository.full_name }}#{{ issue.number }}

{{ issue.title|trim|truncate }}

{{ issue.html_url }}
'''

__pull_request = '''
{{ sender.login }} {{ action }} pull-request {{ repository.full_name }}#{{ pull_request.number }}

{{ pull_request.title|trim|truncate }}

{{ pull_request.html_url }}
'''

__pull_request_review = '''
{%- if action == 'submitted' -%}
{%- if review.state == 'commented' and not review.body  -%}
{%- else -%}
{{ sender.login }} {{ action }} {{ review.state }}-review on {{ repository.full_name }}#{{ pull_request.number }}
{% if review.body %}
{{ review.body|trim|truncate }}
{% endif %}
{{ review.html_url }}
{%- endif -%}
{%- elif action == 'dismissed' -%}
{{ review.user.login }}’s {{ review.state }}-review on {{ repository.full_name }}#{{ pull_request.number }} was dismissed

{{ review.html_url }}
{%- endif -%}
'''

__pull_request_review_comment = '''
{{ sender.login }} {{ action }} comment on pull-request {{ repository.full_name }}#{{ pull_request.number }}

{{ comment.body|trim|truncate }}

{{ comment.html_url }}
'''

__push = '''
{%- if commits|length > 0 -%}
{%- set rest_commits_length = commits|length - 3 -%}
{{ sender.login }} pushed to {{ ref|simplify_branch }} at {{ repository.full_name }}
{% for commit in commits %}
{%- if loop.index <= 3 %}
  - {{ commit.message|trim|truncate(30) }} ({{ commit.id|truncate(7, True, '') }})
{%- endif %}
{%- endfor %}
{%- if rest_commits_length > 0 %}
  ... {{ rest_commits_length }} more commit{% if rest_commits_length > 1 %}s{% endif %}
{%- endif %}

{{ compare }}
{%- endif -%}
'''

__dict = locals()


def get(event):
    return __dict.get('__' + event, '')
