class FileMissingColumn(Exception):
    """Exception raised for missing cols in file.
    """

    def __init__(self, message="Missing required columns from given file."):
        self.message = message
        super().__init__(self.message)
