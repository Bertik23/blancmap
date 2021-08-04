class UserNotExistent(BaseException):
    def __init__(self, id):
        super().__init__(f"User with {id = } does not exist.")


class ToManyMaps(BaseException):
    def __init__(self):
        super().__init__(f"Query returned more maps, than it should.")
