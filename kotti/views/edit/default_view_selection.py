# -*- coding: utf-8 -*-

from kotti.util import _
from pyramid.compat import map_
from pyramid.httpexceptions import HTTPFound
from pyramid.interfaces import IView
from pyramid.interfaces import IViewClassifier
from pyramid.threadlocal import get_current_registry
from pyramid.view import view_config
from pyramid.view import view_defaults
from zope.interface import providedBy


@view_defaults(permission='edit')
class DefaultViewSelection(object):

    def __init__(self, context, request):

        self.context = context
        self.request = request

    def _get_view(self, view_name):  # pragma: no cov
        """This code is copied from pyramid.view.
           We trust it and don't test.

           Returns True if a view with name view_name is registered for context.
        """

        provides = [IViewClassifier] + map_(
            providedBy,
            (self.request, self.context)
        )

        try:
            reg = self.request.registry
        except AttributeError:
            reg = get_current_registry()

        return reg.adapters.lookup(provides, IView, name=view_name)

    def _is_valid_view(self, view_name):
        """Return True if a view with name view_name is registered for context.
        """

        return self._get_view(view_name) is not None

    @view_config(name='default-view-selector',
                 renderer='kotti:templates/default-view-selector.pt')
    def default_view_selector(self):
        """Submenu for selection of the node's default view.
        """

        sviews = [
            {
                "name": v[0],
                "title": v[1],
                "is_current": v[0] == self.context.default_view,
            }
            for v in getattr(self.context.type_info, "selectable_default_views", [])
        ]

        return {
            "selectable_default_views": [
                {
                    "name": "default",
                    "title": _("Default view"),
                    "is_current": self.context.default_view is None,
                }
            ] + sviews,
        }

    @view_config(name='set-default-view')
    def set_default_view(self):
        """Set the node's default view and redirect to it.
        """

        if 'view_name' in self.request.GET:

            view_name = self.request.GET['view_name']

            if view_name == "default":
                self.context.default_view = None
                self.request.session.flash(
                    _("Default view has been reset to default."),
                    'success'
                )
            else:
                if self._is_valid_view(view_name):
                    self.context.default_view = view_name
                    self.request.session.flash(
                        _("Default view has been set."),
                        'success'
                    )
                else:
                    self.request.session.flash(
                        _("Default view could not be set."),
                        'error'
                    )

        return HTTPFound(
            location=self.request.resource_url(self.context)
        )
