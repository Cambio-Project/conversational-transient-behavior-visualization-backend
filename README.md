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

I recommend to host the application on Heroku, as the project is already configured for that environment.
If you need help with Django, check out this resource: [Documentation](https://docs.djangoproject.com/en/3.1/).

# Import Datasets
I used six datasets for my thesis, you can find them in the ```data``` directory. Three datasets belong to a mockup accounting payroll system, the other three datasets belong to SockShop. The data is saved in csv files. I wrote two python scripts that you can use to store the data in the database. One is for the accounting system data, one for the SockShop data:
 
 - ```import_accounting_data.py```
 - ```import_sockshop_data.py```
 
 How to import the data:
 1. Configure in the respective script which dataset you want to important by changing the following variables accordingly: ```SCENARIO```, ```FILE_PATH```
 2. Start the Django shell via
 
    ```python manage.py shell```
   
 3. Execute the script with the following command:
    
    ```exec(open('import_<system>_data.py').read())```
 
 4. The script will create the data objects in the database and show the progress in the terminal.
