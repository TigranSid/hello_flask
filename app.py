#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
   return "Ceci est la page d'accueil."
   
@app.route('/hello/<phrase>')
def hello(phrase):
   return phrase