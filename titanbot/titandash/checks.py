from django.core.checks import Error, Tags, register

from titandash.bot.core.decorators import BotProperty


@register(Tags.compatibility)
def check_bot_properties(app_configs, **kwargs):
    """
    Perform system check to ensure that our bot properties are being used as intended within the bot implementation.

      - A property should enforce "unique" shortcuts, as in, if two properties contain the same shortcut, we should
        error out until it is fixed.

      - A property should not set the queueable and forceable argument when initialized. More checks
        can be added and enforced as needed.

    """
    def _duplicates(lst, key, condense=False):
        """
        Check the parsed list (check) taken from the specified "lst" for duplicate values.

        :param lst: List of bot properties values.
        :param key: Key used to create a list of potential duplicates.
        :param condense: Should the final results dictionary be condensed to only return keys.
        """
        check = [prop[key] for prop in lst]
        d = {}

        for element in check:
            if element not in d:
                if check.count(element) > 1:
                    funcs = []
                    # Loop through each list element again, finding the "key" and adding it
                    # to our results if it matches the current element.
                    for i in lst:
                        if i[key] == element:
                            funcs.append(i["name"])

                    # Append a listified set, to avoid duplicate keys, since the "element" contains the
                    # proper key with the most information.
                    d[element] = list(set(funcs))

        # Returning either a list with duplicates or an empty list,
        # truthy checks will now work correctly.
        if condense:
            return {
                func for func in d
            }
        else:
            return d

    errors = []

    shortcuts = BotProperty.shortcuts()
    queueables = BotProperty.queueables(forceables=True)

    # Checking for any derived bot properties that contain duplicate shortcut values.
    # A single shortcut can only be used once, otherwise the bot will likely just queue
    # up the first found function, which we do not want.
    shortcut_duplicates = _duplicates(
        lst=shortcuts,
        key="shortcut"
    )

    if shortcut_duplicates:
        errors.append(Error(
            msg="Duplicate Shortcuts",
            hint="Duplicate shortcuts found within defined bot properties: (%s)" % shortcut_duplicates,
            obj=None,
            id="titandash.E001"
        ))

    # Checking for any derived bot properties that have specified both the queueable parameter, and forceable,
    # since a forceable function is technically a queueable, there's no need to include both arguments.
    queueables_duplicated = _duplicates(
        lst=queueables,
        key="name",
        condense=True
    )

    if queueables_duplicated:
        errors.append(Error(
            msg="Duplicate Queueables/Forceables",
            hint="Duplicate queueables or forceables found within defined bot properties: (%s)" % queueables_duplicated,
            obj=None,
            id="titandash.E002"
        ))

    return errors
