from archiver import celery


class DebugArchiver(object):
    def __init__(self, *_, **__):
        pass

    def clone(self):
        return self.pointless.si(self)

    @celery.task
    def pointless(self):
        pass
