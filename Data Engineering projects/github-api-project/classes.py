class ValidationResult:
    def __init__(self, status: str, issues: dict = dict(), errors: list = []):
        self.__status = status
        self.__issues = issues
        self.__errors = errors
        pass

    def __repr__(self):
        class_name = type(self).__name__
        return f"{class_name}(status={self.__status!r}, issues={self.__issues!r})"
    
    def __eq__(self, other):
        if not isinstance(other, ValidationResult):
            return NotImplemented

        return (
            self.__status == other.__status
            and self.__issues == other.__issues
        )

    def get_status(self):
        return self.__status

    def is_valid(self):
        return True if self.__status in ["VALID", "VALID_WITH_WARNING"] else False
    
    def invalidate(self):
        self.__status = "INVALID"
    
    def show_issues(self):
        return self.__issues
    
    def update_issues(self, new_issues: dict):
        self.__issues.update(new_issues)
        
    def show_errors(self):
        return self.__errors
