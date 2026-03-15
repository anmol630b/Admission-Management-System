content = open('collage_website/settings.py').read()

old = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""

new = """import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}"""

if old in content:
    content = content.replace(old, new)
    open('collage_website/settings.py', 'w').write(content)
    print('Done!')
else:
    print('Pattern not found - showing line 60-68:')
    lines = content.split('\n')
    for i, line in enumerate(lines[58:70], 59):
        print(f"{i}: {line}")
