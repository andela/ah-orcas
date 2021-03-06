import json

from rest_framework.renderers import JSONRenderer


class AuthorsJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    object_label = 'object'

    def render(self, data, media_type=None, renderer_context=None):
        """
        Check that the JSONRenderer handles the rendering
         of the errors that are thrown from the views
        """
        errors = data.get('errors', None)

        if errors is not None:
            return super(AuthorsJSONRenderer, self).render(data)

        return json.dumps({
            self.object_label: data
        })
