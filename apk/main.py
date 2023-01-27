from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
import copy

from kivy.uix.boxlayout import BoxLayout


class MainApp(App):
    _GATEWAY = "a"
    def build(self):
        self._GATEWAY = "127.0.0.1"
        self.main_layout = BoxLayout(orientation="vertical")

        self.symbol_label = Label(text='DeadNet',
                                  bold=True,
                                  size_hint=(.5, .5),
                                  font_size=100,
                                  pos_hint={'center_x': .5, 'center_y': 1},
                                  color=(237 / 255, 142 / 255, 43 / 255, 0.4))
        self.main_layout.add_widget(self.symbol_label)  # add price label
        self.button_test = Button(text='Start',
                                     size_hint=(None, None),
                                     size=(170, 170),
                                     pos_hint={'center_x': .5, 'center_y': .5})
        self.button_test.bind(on_press=self.on_start_press)
        self.main_layout.add_widget(self.button_test)
        self.gateway = None

        # textinputs = TextInput(text='Hello world', multiline=False)
        # textinputs.bind()
        # self.main_layout.add_widget(textinputs)
        x = self._GATEWAY
        textinput = TextInput(text=x, multiline=False)
        textinput.bind(text=self.on_text)
        self.main_layout.add_widget(textinput)

        return self.main_layout
    def on_text(self, instance, value):
        self.gateway=value
        print(f'gateway -> { self.gateway}')
    def on_start_press(self, instance):
        print("test")
    def on_enter(self, instance, value=None):
        print('User pressed enter in', instance)
        print("-> " + self.gateway)



if __name__ == "__main__":
    app = MainApp()
    app.run()