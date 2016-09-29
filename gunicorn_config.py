import multiprocessing

bind = '0.0.0.0:8080'
workers = multiprocessing.cpu_count() * 2 + 1
daemon = True
pidfile = 'app.pid'
accesslog = 'access.log'
errorlog = 'error.log'
