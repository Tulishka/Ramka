import math
from typing import Dict, List, Union
import pygame


class InputControl:
    def __init__(self, name: str):
        self.name = name
        self.value = 0

    def before_update(self):
        pass

    def update(self, value, deltaTime: float, type='key') -> bool:
        self.value = value
        return bool(value)

    def after_update(self):
        pass


class Axis(InputControl):
    def __init__(self, name: str, scale_value: float = 1.0, full_time=0.2):
        super().__init__(name)

        self.target_value = 0
        self.deltaTime = 0
        self.touches = 0

        self.scale_value = scale_value
        self.axis_speed = self.scale_value / full_time if full_time != 0 else -1

    def before_update(self):
        self.target_value = 0
        self.touches = 0

    def after_update(self):
        if self.value != self.target_value:
            delta = self.target_value - self.value
            if round(abs(delta) * 1000) == 0 or self.axis_speed < 0:
                self.value = self.target_value
            else:
                self.value += math.copysign(min(self.axis_speed * self.deltaTime, abs(delta)), delta)

    def update(self, value, deltaTime: float, type='key') -> bool:
        self.deltaTime = deltaTime
        self.target_value += value * self.scale_value
        if abs(self.target_value) > abs(self.scale_value):
            self.target_value = math.copysign(abs(self.scale_value), self.target_value)
        # if value == 0 and self.axis_speed < 0:
        #     self.value = self.target_value = 0

        self.touches += bool(value)
        return False


class Trigger(InputControl):
    def __init__(self, name: str):
        super().__init__(name)


class Binding:
    def __init__(self, control: InputControl, value, control_type):
        self.control = control
        self.value = value
        self.type = control_type

    def update_control(self, deltaTime: float) -> bool:
        return bool(self.control.update(self.value, deltaTime, self.type))


class KeyBinding(Binding):
    def __init__(self, control: InputControl, value, key):
        super().__init__(control, value, 'key')
        self.key = key

    def update_control(self, deltaTime: float) -> bool:
        return bool(self.control.update(self.value * Input.raw_keys[self.key], deltaTime, self.type))


class JoyKeyBinding(Binding):
    def __init__(self, control: InputControl, joy_num: int, btn_num: int, value):
        super().__init__(control, value, 'key')
        self.joy_num = joy_num
        self.btn_num = btn_num

    def update_control(self, deltaTime: float) -> bool:
        return bool(self.control.update(self.value * Input.raw_joy[self.joy_num].get_button(self.btn_num), deltaTime,
                                        self.type))


class JoyAxesBinding(Binding):
    def __init__(self, control: InputControl, joy_num: int, axis_num: int):
        super().__init__(control, 0, 'axis')
        self.joy_num = joy_num
        self.axis_num = axis_num

    def update_control(self, deltaTime: float) -> bool:
        return bool(self.control.update(round(Input.raw_joy[self.joy_num].get_axis(self.axis_num), 6), deltaTime,
                                        self.type))


class Input:
    control: Dict[str, InputControl] = {}
    binding: List[Binding] = []

    pygame.joystick.init()

    raw_keys = []
    raw_joy = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]

    for i in raw_joy:
        i.init()

    @staticmethod
    def bind_key(control: Union[str, InputControl], key: int, value=1):
        if type(control) == str:
            control = Input.control[control]

        xx = list(filter(lambda x: isinstance(x, KeyBinding) and x.key == key and x.control == control, Input.binding))
        if len(xx):
            Input.binding.remove(xx[0])
        Input.binding.append(KeyBinding(control, value, key))

    @staticmethod
    def bind_joy_btn(control: Union[str, InputControl], joystick_number: int, button: int, value=1):
        if type(control) == str:
            control = Input.control[control]

        xx = list(
            filter(lambda x: isinstance(x,
                                        JoyKeyBinding) and x.joy_num == joystick_number and x.btn_num == button and x.control == control,
                   Input.binding))
        if len(xx):
            Input.binding.remove(xx[0])

        Input.binding.append(JoyKeyBinding(control, joystick_number, button, value))

    @staticmethod
    def bind_joy_axis(control: Union[str, InputControl], joystick_number: int, axis: int):
        if type(control) == str:
            control = Input.control[control]

        xx = list(
            filter(lambda x: isinstance(x,
                                        JoyAxesBinding) and x.joy_num == joystick_number and x.axis_num == axis and x.control == control,
                   Input.binding))
        if len(xx):
            Input.binding.remove(xx[0])

        Input.binding.append(JoyAxesBinding(control, joystick_number, axis))

    @staticmethod
    def update(deltaTime: float):
        from .game import Game
        Input.raw_keys = pygame.key.get_pressed()
        for c in Input.control.values():
            c.before_update()
            for b in filter(lambda x: x.control == c, Input.binding):
                if b.update_control(deltaTime):
                    break
            c.after_update()

        # Game.debug_str=str([Input.raw_joy[0].get_button(i) for i in range(Input.raw_joy[0].get_numbuttons())]);

    @classmethod
    def add_key(cls, name: str):
        c = Trigger(name)
        Input.control[name] = c
        return c

    @classmethod
    def add_axis(cls, name: str, travel_time=0.2, scale=1.0):
        a = Axis(name, scale, travel_time)
        Input.control[name] = a
        return a

    @classmethod
    def info(cls):
        res = ""
        for n, c in Input.control.items():
            res += f'{n}: {round(c.value, 2)} '

        return res

    @classmethod
    def get(cls, name: str):
        if name in Input.control:
            return Input.control[name].value


a = Input.add_key("Jump")
Input.bind_key(a, pygame.K_SPACE)
Input.bind_joy_btn(a, 0, 0)

a = Input.add_axis("Vertical", 0.1)
Input.bind_key(a, pygame.K_w, -1)
Input.bind_key(a, pygame.K_UP, -1)
Input.bind_key(a, pygame.K_s)
Input.bind_key(a, pygame.K_DOWN)

Input.bind_joy_axis(a, 0, 1)

a = Input.add_axis("Horizontal", 0.1)
Input.bind_key(a, pygame.K_d)
Input.bind_key(a, pygame.K_RIGHT)
Input.bind_key(a, pygame.K_a, -1)
Input.bind_key(a, pygame.K_LEFT, -1)
Input.bind_joy_axis(a, 0, 0)
