# -*- coding: utf-8 -*-

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']
CELERY_TIMEZONE = 'Asia/Shanghai'
#如果设置为 False，则表示使用本地时间。在大多数情况下，将其设置为 False 即可。这样可以避免时间显示上的混乱，也方便进行调试和日志记录。
CELERY_ENABLE_UTC = False