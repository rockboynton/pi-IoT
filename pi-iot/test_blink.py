from gpiozero import Button, LED, LEDBoard
from time import sleep

# leds = LEDBoard(6, 13, 12, 26, 20, 21, 4, active_high=False)
# button = Button(16, pull_up=False)
led = LED(6, active_high=False)
led.on()
# print(len(leds))
while True:
    # if button.is_pressed:
    #     led.on()
    # else:
    #     led.off()
    pass