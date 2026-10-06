"""
Configurações do projeto Merenda na Medida.
Tudo que muda entre máquina/produção vem de variáveis de ambiente (.env). Ver ADR-0003.
"""
from pathlib import Path
import os
from datetime import time

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "troque-no-.env")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # apps do projeto (um por domínio — ADR-0001)
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "contas",
    "cardapio",
    "confirmacoes",
    "avaliacoes",
    "painel",
    "api",
    "bot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "merenda.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "merenda.wsgi.application"

# ADR-0003: DATABASE_URL vazio -> SQLite local; em produção aponta pro Neon (Postgres)
_database_url = os.getenv("DATABASE_URL", "").strip()
if _database_url:
    DATABASES = {"default": dj_database_url.parse(_database_url, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Usuário customizado DESDE A PRIMEIRA MIGRATION (contas/models.py)
AUTH_USER_MODEL = "contas.Usuario"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- Regras de negócio (ADR-0008) ----
# Até que horas o aluno pode mudar a confirmação do dia. Formato HH:MM.
_h, _m = os.getenv("HORARIO_CORTE", "16:00").split(":")
HORARIO_CORTE = time(int(_h), int(_m))
# A partir de que horas o jantar de hoje pode ser avaliado (jantar é servido às 20:40).
_h, _m = os.getenv("HORARIO_JANTAR", "20:40").split(":")
HORARIO_JANTAR = time(int(_h), int(_m))

# ---- API (ADR-0005): DRF + JWT; o bot é o único cliente ----
from datetime import timedelta  # noqa: E402

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),   # o bot renova 2x/dia
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Merenda na Medida — API",
    "DESCRIPTION": "Consumida pelo bot do Telegram: cardápio, confirmação de presença e vínculo de conta.",
    "VERSION": "1.0.0",
}
BOT_USERNAME = os.getenv("BOT_USERNAME", "bot")   # usuário de serviço que a API aceita
VINCULO_VALIDADE_MINUTOS = 10

# ---- Integrações (preenchidas nas sprints 2-4) ----
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")  # S4 — ADR-0006
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
