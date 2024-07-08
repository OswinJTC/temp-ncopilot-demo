class DataInterface:
    def execute(self, *args, **kwargs):
        raise NotImplementedError("This method should be overridden by subclasses")
