### translations

1. Add keys: _('key')
2. run: `python manage.py makemessages --all` to generate key-values for all languages
3. Add translations to the generated keys
4. run: `python manage.py compilemessages` to compile
5. To add new languages: add at bottom of settings.py and language_picker.html
6. E.g. if spanish is the new language, run: `python manage.py makemessages -l es` to generate .po files


