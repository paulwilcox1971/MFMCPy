# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 13:13:32 2023

@author: mepdw
"""
from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'