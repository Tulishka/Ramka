from ramka import GameObject, Game, Input, Vector


class CameraInterface:
    def set_focus(self, focus_object, lock_x=False, lock_y=False):
        pass

    def mouse_world_pos(self) -> Vector:
        pass


class Camera(CameraInterface, GameObject):
    main: CameraInterface = None

    def __init__(self, target=None, lock_x=False, lock_y=False):
        super().__init__()
        self._focus = target
        self.lock_x = lock_x
        self.lock_y = lock_y
        if Camera.main is None:
            Camera.main = self

    @property
    def target(self) -> GameObject:
        return self._focus

    def set_focus(self, focus_object, lock_x=False, lock_y=False):
        self._focus = focus_object
        self.lock_x = lock_x
        self.lock_y = lock_y

    def mouse_world_pos(self) -> Vector:
        return self.transform.sub_from_vector(Input.mouse_pos)

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self._focus:
            c = 0.5 * Game.screen_size
            wt = self._focus.screen_pos() - self.screen_pos()
            wt = c - wt
            if not self.lock_x:
                self.transform.x = wt.x

            if not self.lock_y:
                self.transform.y = wt.y

    def on_enter_game(self):
        for o in Game.gameObjects:
            if o != self:
                self.on_newbie(o)

    @Game.on_other_enter_game
    def on_newbie(self, obj):
        if not obj.transform.parent and obj.layer != Game.uiLayer:
            obj.transform.set_parent(self)
