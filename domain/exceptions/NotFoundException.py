class NotFoundException(Exception):
    def __init__(self, resource: str, identifier: str, message: str = None):
        if message is None:
            message = f"{resource} with identifier '{identifier}' was not found."
        super().__init__(message)
        self.resource = resource
        self.identifier = identifier
        self.message = message

    def __str__(self):
        return self.message