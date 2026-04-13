#!/usr/bin/env python
"""创建护工评价表"""
from app import create_app
from app.extensions import db

app = create_app('default')

with app.app_context():
    from app.models import WorkerEvaluation
    db.create_all()
    print('护工评价表创建成功！')
