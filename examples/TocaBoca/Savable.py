import uuid


class Savable:

    def get_uuid(self):
        if not hasattr(self,"uuid"):
            self.uuid = str(uuid.uuid4())

        return self.uuid

    def get_init_dict(self):
        return {}

