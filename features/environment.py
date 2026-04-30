"""
Behave ortam yapılandırması - her senaryo öncesi veritabanını temizler.
"""
import django
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_ra_saas.settings')


def before_all(context):
    django.setup()
    from django.test.utils import setup_test_environment
    setup_test_environment()


def before_scenario(context, scenario):
    from django.test.runner import DiscoverRunner
    context.runner = DiscoverRunner(verbosity=0)
    context.old_config = context.runner.setup_databases()
    context._count_before = 0


def after_scenario(context, scenario):
    context.runner.teardown_databases(context.old_config)
