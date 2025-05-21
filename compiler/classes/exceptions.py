class ReturnException(Exception):
    def __init__(self, value, type_):
        super().__init__('Return')
        self.value = value
        self.type_ = type_