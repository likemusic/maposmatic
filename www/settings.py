# coding: utf-8

# maposmatic, the web front-end of the MapOSMatic city map generation system
# Copyright (C) 2009  David Decotigny
# Copyright (C) 2009  Frédéric Lehobey
# Copyright (C) 2009  David Mentré
# Copyright (C) 2009  Maxime Petazzoni
# Copyright (C) 2009  Thomas Petazzoni
# Copyright (C) 2009  Gaël Utard

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Django settings for www project.

import logging
import os.path

from django.utils.translation import ugettext_lazy as _

from .settings_local import *
from . import logconfig

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# ADMIN_MEDIA_PREFIX = '/admin-media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'tm+wb)lp5q%br=p0d2toz&km_-w)cmcelv!7inons&^v9(q!d2'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_PATH, 'templates'),
            os.path.join(PROJECT_PATH, 'maposmatic/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'www.maposmatic.context_processors.all',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'www.urls'

LOCAL_MEDIA_PATH = os.path.join(PROJECT_PATH, 'static')

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'www.maposmatic',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Available website translations. Note that the language codes must be
# specified in Django i18n location (all lowercase, with the language and
# locale separated by a dash instead of an underscore: pt_BR -> pt-br)
LANGUAGES = {
    "fr":    "Français",
    "en":    "English",
    "de":    "Deutsch",
    "it":    "Italiano",
    "ca":    "Català",
    "ru":    "Русский",
    "ar":    "العربية",
    "pt-pt": "Português",
    "pt-br": "Português do Brasil",
    "nb":    "Norwegian Bokmål",
    "nl":    "Nederlands",
    "hr":    "Hrvatski",
    "pl":    "Polski",
    "es":    "Español",
    "id":    "Bahasa Indonesia",
    "tr":    "Türkçe",
    "ja":    "日本人",
    "el":    "ελληνικά",
    "be":    "беларуская",
    "uk":    "українська",
    "hu":    "Hungarian",
    "zh-tw": "繁體中文",
    "fa":    "فارسی",
}
LANGUAGES_LIST = sorted(LANGUAGES.items(), key=lambda p: p[1])

# Associate a Django language code with:
#  the language code used to select the Paypal button
#  the country code that allows to get the proper translation of the
#  PayPal payment page
# When no association is found, we automatically default to english
PAYPAL_LANGUAGES = {
    "fr": ("fr_FR", "FR"),
    "de": ("de_DE", "DE"),
    "it": ("it_IT", "IT"),
    "pt-pt": ("pt_PT", "PT"),
    "pt-br": ("pt_BR", "BR"),
    "nl": ("nl_NL", "NL"),
    "pl": ("pl_PL", "PL"),
    "es": ("es_ES", "ES"),
    "el": ("el_GR", "GR"),
}

# Languages must be ordered by country (in xx_YY, YY is the country
# code), and then ordered with the most widely used language in the
# country first. For example, in France, we will want "French" to be
# the first, and catalan to be in the second place). The reason for
# this is that the order in the below list will be the order with
# which languages will be presented by the MapOSMatic website (after
# filtering the language list based on the country of the city that is
# being rendered).
MAP_LANGUAGES = {
    "ca_AD.UTF-8": "Andorra (CA)",
    "ar_AE.UTF-8": "دولة الإمارات العربية المتحدة (AR)",
    "en_AG":       "Antigua and Barbuda (EN)",
    "es_AR.UTF-8": "Argentina (ES)",
    "de_AT.UTF-8": "Österreich (DE)",
    "en_AU.UTF-8": "Australia (EN)",
    "nl_BE.UTF-8": "Koninkrijk België (NL)",
    "fr_BE.UTF-8": "Royaume de Belgique (FR)",
    "de_BE.UTF-8": "Königreich Belgien (DE)",
    "ar_BH.UTF-8": "البحرين (AR)",
    "be_BY.UTF-8": "Белару́сь (BY)",
    "es_BO.UTF-8": "Bolivia (ES)",
    "pt_BR.UTF-8": "Brasil (PT)",
    "en_BW.UTF-8": "Botswana (EN)",
    "en_CA.UTF-8": "Canada (EN)",
    "fr_CA.UTF-8": "Canada (FR)",
    "de_CH.UTF-8": "Schweiz (DE)",
    "fr_CH.UTF-8": "Suisse (FR)",
    "it_CH.UTF-8": "Svizzera (IT)",
    "el_GR.UTF-8": "Ελλάδα (GR)",
    "es_CL.UTF-8": "Chile (ES)",
    "es_CR.UTF-8": "Costa Rica (ES)",
    "de_DE.UTF-8": "Deutschland (DE)",
    "da_DK.UTF-8": "Danmark (DA)",
    "en_DK.UTF-8": "Denmark (EN)",
    "es_DO.UTF-8": "República Dominicana (ES)",
    "ar_DZ.UTF-8": "الجزائر (AR)",
    "es_EC.UTF-8": "Ecuador (ES)",
    "ar_EG.UTF-8": "مصر (AR)",
    "es_ES.UTF-8": "España (ES)",
    "ca_ES.UTF-8": "Espanya (CA)",
    "ast_ES.UTF-8": "España (AST)",
    "fr_FR.UTF-8": "France (FR)",
    "ca_FR.UTF-8": "França (CA)",
    "en_GB.UTF-8": "United Kingdom (EN)",
    "es_GT.UTF-8": "Guatemala (ES)",
    "en_HK.UTF-8": "Hong Kong (EN)",
    "es_HN.UTF-8": "Honduras (ES)",
    "hr_HR.UTF-8": "Republika Hrvatska",
    "id_ID.UTF-8": "Bahasa Indonesia (ID)",
    "en_IE.UTF-8": "Ireland (EN)",
    "en_IN":       "India (EN)",
    "ar_IQ.UTF-8": "العراق (AR)",
    "it_IT.UTF-8": "Italia (IT)",
    "ar_JO.UTF-8": "الأردنّ‎ (AR)",
    "ar_KW.UTF-8": "الكويت (AR)",
    "ar_LB.UTF-8": "لبنان (AR)",
    "ja_JP.UTF-8": "日本人 (JA)",
    "fr_LU.UTF-8": "Luxembourg (FR)",
    "de_LU.UTF-8": "Luxemburg (DE)",
    "ar_LY.UTF-8": "ليبيا (AR)",
    "ar_MA.UTF-8": "المملكة المغربية (AR)",
    "es_MX.UTF-8": "México (ES)",
    "en_NG":       "Nigeria (EN)",
    "es_NI.UTF-8": "Nicaragua (ES)",
    "nl_NL.UTF-8": "Nederland (NL)",
    "nb_NO.UTF-8": "Norwegian Bokmål (NO)",
    "nn_NO.UTF-8": "Norwegian Nynorsk (NO)",
    "en_NZ.UTF-8": "New Zealand (EN)",
    "ar_OM.UTF-8": "سلطنة عمان (AR)",
    "es_PA.UTF-8": "Panamá (ES)",
    "es_PE.UTF-8": "Perú (ES)",
    "en_PH.UTF-8": "Philippines (EN)",
    "pl_PL.UTF-8": "Rzeczpospolita Polska",
    "pt_PT.UTF-8": "Portugal (PT)",
    "es_PR.UTF-8": "Puerto Rico (ES)",
    "es_PY.UTF-8": "Paraguay (ES)",
    "ar_QA.UTF-8": "دولة قطر (AR)",
    "ro_RO.UTF-8": "Românesc (RO)",
    "ru_RU.UTF-8": "Русский",
    "ar_SA.UTF-8": "المملكة العربية السعودية (AR)",
    "ar_SD.UTF-8": "السودان (AR)",
    "en_SG.UTF-8": "Singapore (EN)",
    "es_SV.UTF-8": "El Salvador (ES)",
    "ar_SY.UTF-8": "سوريا (AR)",
    "ar_TN.UTF-8": "تونس (AR)",
    "en_US.UTF-8": "United States (EN)",
    "es_US.UTF-8": "Estados Unidos de América (ES)",
    "uk_UA.UTF-8": "Україна (UK)",
    "es_UY.UTF-8": "Uruguay (ES)",
    "es_VE.UTF-8": "Venezuela (ES)",
    "ar_YE.UTF-8": "اليَمَن (AR)",
    "en_ZA.UTF-8": "South Africa (EN)",
    "en_ZW.UTF-8": "Zimbabwe (EN)",
    "tr_TR.UTF-8": "Türkçe (TR)",
    "sk_SK.UTF-8": "Slovakien (SK)",
    "hu_HU.UTF-8": "Hungarian (HU)",
    "fa_IR.UTF-8": "فارسی (FA)",
#    "C": _(u"No localization"),
}

MAP_LANGUAGES_LIST = sorted(MAP_LANGUAGES.items(), key=lambda p: p[1])
MAP_LANGUAGES_LIST.append(("C", _(u"No localization")))

# GIS database (read settings from OCitySMap's configuration). The
# default port to connect to the database is 5432, which is the
# default PostgreSQL port.
import configparser
gis_config = configparser.SafeConfigParser({'port': '5432'})

if OCITYSMAP_CFG_PATH is None:
    OCITYSMAP_CFG_PATH = os.path.expanduser('~/.ocitysmap.conf')
with open(OCITYSMAP_CFG_PATH, encoding='utf-8') as fp:
    gis_config.readfp(fp)
GIS_DATABASE_HOST = gis_config.get('datasource', 'host')
GIS_DATABASE_USER = gis_config.get('datasource', 'user')
GIS_DATABASE_PASSWORD = gis_config.get('datasource', 'password')
GIS_DATABASE_NAME = gis_config.get('datasource', 'dbname')
GIS_DATABASE_PORT = gis_config.get('datasource', 'port')

def has_gis_database():
    return GIS_DATABASE_NAME and GIS_DATABASE_NAME != ''

# Job page refresh frequency, in seconds, for when the job is waiting in queue
# and when the job is currently being rendered.
REFRESH_JOB_WAITING = 15
REFRESH_JOB_RENDERING = 10

def is_daemon_running():
    return 0 == os.system('systemctl is-active maposmatic-render.service')

# Logging
logconfig.setup_maposmatic_logging(
        int(os.environ.get("MAPOSMATIC_LOG_LEVEL",
                           DEFAULT_MAPOSMATIC_LOG_LEVEL)),
        os.environ.get('MAPOSMATIC_LOG_FILE', DEFAULT_MAPOSMATIC_LOG_FILE),
        os.environ.get("MAPOSMATIC_LOG_FORMAT", DEFAULT_MAPOSMATIC_LOG_FORMAT))
LOG = logging.getLogger('maposmatic')

# File upload settings

# make sure that files that exceed FILE_UPLOAD_MAX_MEMORY_SIZE
# are still readable 
FILE_UPLOAD_PERMISSIONS = 0o644


