import json
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from authors.apps.core.renderers import AuthorsJSONRenderer


class CommentsRenderer(AuthorsJSONRenderer):
    charset = 'utf-8'
    object_name = 'comments'

    def render(self, data, media_type=None, renderer_context=None):
        """
        Check that the JSONRenderer handles the rendering
         of the errors that are thrown from the views
        """
        errors = data
        if errors is not None:
            return super(AuthorsJSONRenderer, self).render(data)

        return json.dumps({
            self.object_label: data
        })


class CommentsThreadsRenderer(AuthorsJSONRenderer):
    charset = 'utf-8'
    object_name = 'threads'


class FavoriteJSONRenderer(JSONRenderer):
    def render(self, data, media_type=None, renderer_context=None):
        if renderer_context:
            status_code = renderer_context.get('response').status_code
            if not status_code == status.HTTP_200_OK:
                return super(FavoriteJSONRenderer, self).render(data)
        return super(FavoriteJSONRenderer, self).render(data)
