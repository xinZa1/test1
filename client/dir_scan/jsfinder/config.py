# -*- coding: utf-8 -*-

#Celery 的配置选项
CELERY_TASK_SERIALIZER = 'json'  #任务序列化器，默认使用的是 pickle。在此处设置为 'json' 表示使用 JSON 格式进行序列化
CELERY_RESULT_SERIALIZER = 'json'   #结果序列化器，默认也是 pickle。在此处设置为 'json' 表示使用 JSON 格式进行序列化
CELERY_ACCEPT_CONTENT=['json']      #指定接受的数据格式列表,在此处设置为 ['json'] 表示只接受 JSON 格式的数据
CELERY_TIMEZONE = 'Asia/Shanghai'   #Celery 的时区设置，默认是 UTC。在此处设置为 'Asia/Shanghai' 表示使用上海时区
CELERY_ENABLE_UTC = False           #是否启用 UTC 时间，默认为 True。在此处设置为 False 表示不启用 UTC 时间