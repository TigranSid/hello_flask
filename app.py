#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Flask, jsonify, request
app = Flask(__name__)
app.secret_key = 34

incomes = [
  { 'description': 'salary', 'amount': 5000 }
]


@app.route('/incomes')
def get_incomes():
  return jsonify(incomes)


@app.route('/incomes', methods=['POST'])
def add_income():
  incomes.append(request.get_json())
  return '', 204

if __name__ == '__main__':
    app.run(debug=True)