0.0.12  2023-07-14
- fixed location of static file notify.js in base template

0.0.13  2023-07-14
- restored reference to vdjango-notifications-hq's notify.js in base template
- fixed django-notifications-hq version in requirements.txt to 1.7.0 - 1.8.0 and 1.8.2 are broken

0.0.14 2023-08-01
- fixed regression error in django-notifications-hq requirements (now ==1.7.0)
- replaced class_name with classname for compatibility with wagtail 6
- misc codespell and flake8 refactorings
