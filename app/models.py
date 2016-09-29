# -*- coding: utf-8 -*-

from .database import db


class Token(db.Model):
    __tablename__ = 'token'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(255), nullable=False, unique=True)
    secret = db.Column(db.String(255), nullable=False, server_default='')
    description = db.Column(db.String(255), nullable=False, server_default='')

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', None)
        self.token = kwargs.get('token', None)
        self.code = kwargs.get('code', None)
        self.secret = kwargs.get('secret', None)
        self.description = kwargs.get('description', None)

    def __repr__(self):
        return '<User id={}, code={}>'.format(self.id, self.code)


class Template(db.Model):
    __tablename__ = 'template'

    token_id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(255), primary_key=True)
    template = db.Column(db.String(1000), nullable=False, server_default='')

    def __init__(self, **kwargs):
        self.token_id = kwargs.get('token_id', None)
        self.event = kwargs.get('event', None)
        self.template = kwargs.get('template', None)

    def __repr__(self):
        return '<Template id={}, token_id={}, event={}>'.format(self.id, self.token_id, self.event)
