'''
    gunicorn启动入口
'''


import gevent.monkey
gevent.monkey.patch_all()

import multiprocessing


debug = False
loglevel = 'debug'
bind = '0.0.0.0:5000'
errorlog = './log/gunicorn.log'

# 超时时间
timeout = 0

# 启动的进程数
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 1

# 使用gevent协程实现高并发
worker_class = 'gunicorn.workers.ggevent.GeventWorker'