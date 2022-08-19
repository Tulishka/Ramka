from ramka import GameObject, Game, Input


class Draggable:

    def is_dragged(self):
        g = Game.get_objects(DragAndDropController)
        for h in g:
            return (h.obj == self)
        return False


class DragAndDropController(GameObject):
    def __init__(self):
        super().__init__()
        self.obj_start_pos = None
        self.drag_start_pos = None
        self.obj = None

    @Game.on_mouse_down(button=1, hover=False)
    def drag_start(self):
        sel = list(Game.get_objects(clas=Draggable))
        sel.reverse()
        for s in sel:
            if s.touch_test(Input.mouse_pos):
                Game.defaultLayer.change_order_last(s)
                z = list(Game.get_objects(clas=Draggable))
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
            self.obj_start_pos = None
            self.drag_start_pos = None
            self.obj = None
