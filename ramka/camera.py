from ramka import GameObject, Game


class Camera(GameObject):

    def __init__(self):
        super().__init__()
        self._focus = None


    def set_focus(self,focus_object):
        self._focus=focus_object

    def update(self, deltaTime: float):
        super().update(deltaTime)

        if self._focus:
            c = 0.5 * Game.screen_size
            wt = self._focus.screen_pos() - self.screen_pos()
            self.transform.xy = c - wt

    def on_enter_game(self):
        for o in Game.gameObjects:
            if o != self:
                self.on_newbie(o)

    @Game.on_other_enter_game
    def on_newbie(self, obj):
        if not obj.transform.parent:
            obj.transform.set_parent(self)

