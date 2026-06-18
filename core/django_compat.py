"""Compatibility fixes for supported local development runtimes."""

from copy import copy


def patch_template_context_copy():
    """
    Make Django template contexts copyable on Python versions where copying
    ``super()`` no longer returns a mutable context instance.

    Django 5.1.2's ``BaseContext.__copy__`` can fail under Python 3.14 with:
    ``AttributeError: 'super' object has no attribute 'dicts'``. The fixed
    implementation below matches newer Django releases and keeps built-in admin
    inclusion tags such as ``submit_row`` working.
    """
    from django.template.context import BaseContext, RenderContext

    def safe_context_copy(self):
        duplicate = BaseContext()
        duplicate.__class__ = self.__class__
        duplicate.__dict__ = copy(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = safe_context_copy
    RenderContext.__copy__ = safe_context_copy


def ensure_local_sqlite_inquiry_schema():
    """
    Repair older local SQLite databases that were created before the
    ``Inquiry.additional_interests`` column existed.

    This project is commonly run as a local demo with the checked-out SQLite
    database. If a developer pulls the new model field but has not run
    ``python manage.py migrate`` yet, posting the chatbot form can crash with
    ``OperationalError: table core_inquiry has no column named
    additional_interests``. The normal fix is still to run migrations, but this
    lightweight compatibility guard keeps existing local demo databases usable
    by adding the missing column idempotently.
    """
    from django.conf import settings
    from django.db import connection
    from django.db.utils import DatabaseError, OperationalError
    from django.utils import timezone

    if not settings.DEBUG or connection.vendor != 'sqlite':
        return

    try:
        existing_tables = connection.introspection.table_names()
        if 'core_inquiry' not in existing_tables:
            return

        with connection.cursor() as cursor:
            columns = [column.name for column in connection.introspection.get_table_description(cursor, 'core_inquiry')]
            if 'additional_interests' in columns:
                return
            cursor.execute("ALTER TABLE core_inquiry ADD COLUMN additional_interests text NOT NULL DEFAULT ''")

            if 'django_migrations' in existing_tables:
                already_recorded = cursor.execute(
                    "SELECT 1 FROM django_migrations WHERE app = %s AND name = %s",
                    ['core', '0002_alter_activity_options_alter_inquiry_options_and_more'],
                ).fetchone()
                if not already_recorded:
                    cursor.execute(
                        "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                        ['core', '0002_alter_activity_options_alter_inquiry_options_and_more', timezone.now()],
                    )
    except (DatabaseError, OperationalError):
        # Do not break startup/check/migrate commands; formal migrations remain
        # the source of truth when the database is not in the expected local
        # SQLite demo state.
        return
