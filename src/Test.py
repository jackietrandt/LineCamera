import kivy
kivy.require('1.6.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button

import cv

class MyApp(App):

    def build(self):
        return Button(text='Hello World')

if __name__ == '__main__':
    MyApp().run()
