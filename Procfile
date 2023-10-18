web: gunicorn we_book.wsgi
dokku post-deploy: python manage.py generate_menus
post-deploy: python manage.py generate_menus
