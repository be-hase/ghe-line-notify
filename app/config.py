# -*- coding: utf-8 -*-

import distutils.util
import os

DEBUG = bool(distutils.util.strtobool(os.getenv('GHE_LN_DEBUG', '0')))
SECRET_KEY = os.getenv('GHE_LN_SECRET_KEY', 'to_be_overridden')
GHE_LN_DATABASE_URI = os.getenv('GHE_LN_DATABASE_URI', None)

SQLALCHEMY_TRACK_MODIFICATIONS = False
