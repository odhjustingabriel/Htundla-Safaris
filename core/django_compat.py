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
