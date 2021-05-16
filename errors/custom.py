class FileMissingColumn(Exception):
    """Exception raised for errors in the input salary.

        Attributes:
            salary -- input salary which caused the error
            message -- explanation of the error
    """

    def __init__(self, message="Missing required columns from given file."):
        self.message = message
        super().__init__(self.message)
