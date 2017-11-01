
def init_test_settings():
    return {

        'CACHES': {
            'default': {
                'django.core.cache.backends.locmem.LocMemCache'
            }
        },

        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'testingdb'
            }
        }
    }
