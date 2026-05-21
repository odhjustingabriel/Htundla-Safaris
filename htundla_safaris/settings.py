import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'unsafe-dev-key-change-me')
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]
INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'core',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware',
    'core.middleware.SecurityHardeningMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'htundla_safaris.urls'
TEMPLATES = [{
    'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'core'/'templates'],'APP_DIRS':True,
    'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}
}]
WSGI_APPLICATION = 'htundla_safaris.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'en-us'; TIME_ZONE='UTC'; USE_I18N=True; USE_TZ=True
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR/'css', BASE_DIR/'js', BASE_DIR/'img']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@htundla.local'

RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get('RATE_LIMIT_WINDOW_SECONDS', '900'))
RATE_LIMIT_DEFAULT_REQUESTS = int(os.environ.get('RATE_LIMIT_DEFAULT_REQUESTS', '120'))
RATE_LIMIT_AUTH_REQUESTS = int(os.environ.get('RATE_LIMIT_AUTH_REQUESTS', '5'))
MAX_PAYLOAD_BYTES = int(os.environ.get('MAX_PAYLOAD_BYTES', '1048576'))

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
