class State:
    def __init__(self,animation: str = "default"):
        self.animation = animation


class StateIdle(State):
    def __init__(self):
        super().__init__("idle")


class StateWalk(State):
    def __init__(self):
        super().__init__("walk")

state_default = State()
state_idle = StateIdle()
state_walk = StateWalk()
