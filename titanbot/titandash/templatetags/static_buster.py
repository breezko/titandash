from django.templatetags.static import StaticNode
from django import template
from django.conf import settings


register = template.Library()


class CacheBusterNode(StaticNode):
    """
    Overriding the default static node functionality to include versioning in static files
    delivered through titandash locally.
    """
    @classmethod
    def handle_simple(cls, path):
        return cls.bust(path=super(CacheBusterNode, cls).handle_simple(path))

    @staticmethod
    def bust(path):
        """
        Include the current titandash version as a simple versioning string in the path provided.
        """
        return "{path}?{version}".format(
            path=path,
            version=settings.BOT_VERSION
        )


@register.tag('static')
def do_static(parser, token):
    return CacheBusterNode.handle_token(parser, token)


def static(path):
    return CacheBusterNode.handle_simple(path)
