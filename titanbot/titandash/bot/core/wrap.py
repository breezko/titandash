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
                    self._check_attr(
                        attr=key
                    )
                    setattr(self, key, value)
                    logger.debug("dynamic attr: {attr} = {value}".format(
                        attr=key,
                        value=value
                    ))
            else:
                self._check_attr(
                    attr=group
                )
                setattr(self, group, d)
                logger.debug("dynamic attr: {attr} = {value}".format(
                    attr=group,
                    value=d
                ))

    def _check_attr(self, attr):
        """
        Perform a check of the specified dynamic attribute. If it already exists on the instance,
        an exception should be raised since it means that a previous attribute would be overwritten.
        """
        try:
            if getattr(self, attr):
                raise ValueError("dynamic attr: \"{attr}\" has already been set, duplicate key found? "
                                 "setting this value would overwrite the previously set attribute with the "
                                 "same name.".format(attr=attr))
        except AttributeError:
            pass

