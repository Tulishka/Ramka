from ramka import GameObject, Game, Vector, Camera, Input


class DragAndDropControllerInterface:
    def get_dragged_object(self):
        pass


class Draggable:

    def is_dragged(self):
        return DragAndDropController.controller and DragAndDropController.controller.get_dragged_object() == self

    def on_drag_start(self):
        return True

    def on_drag_end(self):
        pass

    def is_inverted_drag(self):
        return False

    def move_me_top(self):
        return True

    def drag_now(self, object: GameObject):
        pass

    def use_world_drag(self):
        return False

    def drag_set_new_position(self, pos: Vector):
        self.transform.pos = pos


class DragAndDropController(DragAndDropControllerInterface, GameObject):
    controller: DragAndDropControllerInterface = None

    def __init__(self):
        super().__init__()
        self.obj_start_pos = None
        self.drag_start_pos = None
        self.obj = None

        DragAndDropController.controller = self

    def get_dragged_object(self):
        return self.obj

    @staticmethod
    def get_mouse(obj):
        if obj.use_world_drag():
            return Input.mouse_pos
        else:
            return Camera.main.mouse_world_pos() if Camera.main else Input.mouse_pos

    def drag_now(self, object):
        if not self.obj:
            if object.move_me_top():
                Game.defaultLayer.change_order_last(object)
            self.drag_start_pos = self.get_mouse(object)
            self.obj_start_pos = object.transform.pos
            self.obj = object

    @Game.on_mouse_down(button=1, hover=False)
    def drag_start(self):
        sel = list(Game.get_objects(clas=Draggable, filter=lambda x: x.visible and x.opacity))
        sel.reverse()
        for s in sel:
            if s.touch_test(Input.mouse_pos):
                ds = s.on_drag_start()
                if ds != False:
                    s = s if not isinstance(ds, GameObject) else ds
                    self.drag_now(s)
                    break

    def __get_delta(self):
        if self.obj:
            delta = self.get_mouse(self.obj) - self.drag_start_pos
            if self.obj.is_inverted_drag():
                delta *= -1
        else:
            delta = Vector(0, 0)

        return delta

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if self.obj:
            self.obj.drag_set_new_position(self.obj_start_pos + self.__get_delta())

    @Game.on_mouse_up(button=1, hover=False)
    def release_mi(self):
        if self.obj:
            self.obj.drag_set_new_position(self.obj_start_pos + self.__get_delta())
            self.obj.on_drag_end()
            self.obj_start_pos = None
            self.drag_start_pos = None
            self.obj = None
