from titandash.models.bot import BotInstance


__base__ = ("fields", "instance")


class Props(object):
    """
    Property container used to encapsulate saving functionality and instance saving into single functions.

    Saving a bot instance handles our websocket implementation signals, so we handle setting and getting
    of properties here.
    """
    def __init__(self, instance):
        """
        Setting up our instance and building out the list of valid properties.
        """
        self.fields = [f.name for f in BotInstance._meta.get_fields() if not f.name.startswith('_')]
        self.instance = instance

    def __getattr__(self, item):
        """
        Custom attribute getter to only ever retrieve values from our base fields (which should be present in our init,
        and the instance specified.
        """
        if item in __base__:
            return super(Props, self).__getattribute__(item)
        if item in self.fields:
            return getattr(self.instance, item)

    def __setattr__(self, key, value):
        """
        Custom attribute setter to ensure our instance is updated and saved when our derived properties
        are set on the Props object.
        """
        if key in __base__:
            super(Props, self).__setattr__(key, value)
        elif key in self.fields:
            # Externally setting the instance value as well, this ensures our
            # sockets are still firing properly when values change.
            setattr(self.instance, key, value)
            # Calling save will actually send the socket signal.
            self.instance.save()
