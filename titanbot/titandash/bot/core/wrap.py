class DynamicAttrs:
    """
    Dynamic allocation of object attributes.
    """
    def __init__(self, attrs, logger):
        self.logger = logger

        # Looping through all values passed in and setting up our attributes.
        # These variables may not be "present" when viewing through an IDE, but
        # attributes getters should work just fine.
        for group, d in attrs.items():
            if isinstance(d, dict):
                for key, value in d.items():
                    setattr(self, key, value)
                    logger.debug("dynamic attr: {attr} = {value}".format(
                        attr=key,
                        value=value
                    ))
            else:
                setattr(self, group, d)
                logger.debug("dynamic attr: {attr} = {value}".format(
                    attr=group,
                    value=d
                ))
