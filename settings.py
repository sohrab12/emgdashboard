# Django settings for emgdashboard project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Sam Kaufman', 'kaufmans@uci.edu'),
    ('Melody Tse', 'mwtse@uci.edu'),
    ('Alex Kaiser', 'adkaiser@uci.edu'),
    ('Josh Villamarzo', 'jvillama@uci.edu'),
    ('Sohrab Hejazi', 'shejazi@uci.edu'),
)
MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'EMGDashboardDB.db'
DATABASE_USER = ''
DATABASE_PASSWORD = ''
DATABASE_HOST = ''
DATABASE_PORT = ''

TIME_ZONE = 'America/Los_Angeles'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/Users/emrys/Code/emgdashboard/static/'  #absolute path to media

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-h4d@0y&u3^711tgu0p9_b54-8nuc53d-20$%8(3r1je)d0qr4'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'emgdashboard.urls'

TEMPLATE_DIRS = (
    "/Users/emrys/Code/emgdashboard/templates",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'emgdashboard.dashboard'
)


# If there is a local_settings module,
# it should be allowed to override the
# above. This is for clean deployment.
try:
    from local_settings import *
except ImportError:
    pass