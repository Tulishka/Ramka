from ramka import GameObject, Game, Input


class DragAndDropControllerInterface:
    def get_dragged_object(self):
        pass


class Draggable:

    def is_dragged(self):
        return DragAndDropController.controller.get_dragged_object() == self

    def on_drag_start(self):
        return True

    def on_drag_end(self):
        pass


class DragAndDropController(DragAndDropControllerInterface, GameObject):
    controller: DragAndDropControllerInterface = None

    def __init__(self):
        super().__init__()
        self.obj_start_pos = None
        self.drag_start_pos = None
        self.obj = None

        if not DragAndDropController.controller:
            DragAndDropController.controller = self

    def get_dragged_object(self):
        return self.obj

    @Game.on_mouse_down(button=1, hover=False)
    def drag_start(self):
        sel = list(Game.get_objects(clas=Draggable, filter=lambda x: x.visible and x.opacity))
        sel.reverse()
        for s in sel:
            if s.touch_test(Input.mouse_pos):
                ds = s.on_drag_start()
                if ds != False:
                    s = s if not isinstance(ds, GameObject) else ds
                    Game.defaultLayer.change_order_last(s)
                    self.drag_start_pos = Input.mouse_pos
                    self.obj_start_pos = s.transform.pos
                    self.obj = s
                    break

    def update(self, deltaTime: float):
        super().update(deltaTime)
        if self.obj:
            self.obj.transform.pos = self.obj_start_pos + Input.mouse_pos - self.drag_start_pos

    @Game.on_mouse_up(button=1, hover=False)
    def release_mi(self):
        if self.obj:
            self.obj.transform.pos = self.obj_start_pos + Input.mouse_pos - self.drag_start_pos
            self.obj.on_drag_end()
            self.obj_start_pos = None
            self.drag_start_pos = None
            self.obj = None
