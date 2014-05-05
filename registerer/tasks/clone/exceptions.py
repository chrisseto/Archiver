class CloningError(Exception):
    def __init__(self, reason):
        self.reason = reason
        self.status_code = 400

    def to_dict(self):
        return {
            'message': self.reason
        }


class AddonCloningError(CloningError):
    pass
