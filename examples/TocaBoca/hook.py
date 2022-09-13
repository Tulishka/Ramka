from interier import Interier


class Hook(Interier):
    def can_accept_dropzone_object(self, dropzone, obj):
        return True
