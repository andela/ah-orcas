import json

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
