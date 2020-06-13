class CommandException(BaseException):
    def __init__(self, message=None, *args):
        if message is not None:
            # clean-up @everyone and @here mentions
            m = message.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
            super().__init__(m, *args)
        else:
            super().__init__(*args)

class CommandInfo(CommandException):
    pass

class CommandError(CommandException):
    pass


class CheckFailure(CommandError):
    pass


class MissingPermissions(CheckFailure):
    """Exception raised when the command invoker lacks permissions to run a
    command.
    This inherits from :exc:`CheckFailure`
    Attributes
    -----------
    missing_perms: :class:`list`
        The required permissions that are missing.
    """

    def __init__(self, missing_perms, *args):
        self.missing_perms = missing_perms

        missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in missing_perms]

        if len(missing) > 2:
            fmt = '{}, and {}'.format(", ".join(missing[:-1]), missing[-1])
        else:
            fmt = ' and '.join(missing)
        message = 'You are missing {} permission(s) to run this command.'.format(fmt)
        super().__init__(message, *args)


class NotWhitelisted(CheckFailure):
    def __init__(self, *args):
        message = 'You are not whitelisted for this command.'
        super().__init__(message, *args)
