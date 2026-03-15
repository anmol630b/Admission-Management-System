content = open('collage_website/settings.py').read()

# Remove the broken part and fix it
bad = """import dj_database_url
import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}"""

good = """import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}"""

if bad in content:
    content = content.replace(bad, good)
    open('collage_website/settings.py', 'w').write(content)
    print('Fixed!')
else:
    print('Showing DATABASES section:')
    for i, line in enumerate(content.split('\n')[58:75], 59):
        print(f"{i}: {line}")
