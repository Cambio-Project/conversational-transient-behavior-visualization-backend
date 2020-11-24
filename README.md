# Setup
1. Install packages

    ```pip install -r requirements.txt```
2. Add database in ./webservice/settings.py
    ```
    DATABASES = {
      'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '<database_name>',
        'HOST': '<database_host>',
        'PORT': 5432,
        'USER': '<database_user>',
        'PASSWORD': '<database_password>'
      }
    }
    ```
 3. Run server
 
    ```python manage.py runserver```
