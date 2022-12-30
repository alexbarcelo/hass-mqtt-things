
class WrapperCallback:
    def __init__(self, callback) -> None:
        self.cb = callback

    def __call__(self, client, userdata, message):
        return self.cb(message.topic, message.payload)
