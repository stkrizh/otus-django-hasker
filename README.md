# otus-django-hasker
Poor Man's Stackoverflow

### Live version
https://hasker.pythonanywhere.com/

### API documentation
https://hasker.pythonanywhere.com/api/v1/swagger-ui/

### Requirements
- Python (3.6+)
- Django (2.2+)
- Django REST framework (3.10+)

### Development environment installation

1. Clone the repository
```
git clone https://github.com/stkrizh/otus-django-hasker.git
cd otus-django-hasker
```

2. Create and activate new virtual environment
```
python3.6 -m virtualenv .env --prompt=HASKER
source .env/bin/activate
```

3. Install requirements
```
pip install -r requirements-dev.txt
```

4. Create (or update) local settings
```
cp local_settings.py.template config/local_settings.py
```

5. Apply migrations
```
python manage.py migrate
```

6. Run tests
```
python manage.py test
```

### Development server
Make sure that virtual environment is activated:
```
cd otus-django-hasker
source .env/bin/activate
```

To run development server:
```
python manage.py runserver
```
