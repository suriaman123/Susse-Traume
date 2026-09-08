# Süße Träume — Night light + spoken message 

from machine import Pin, ADC, UART          # UART = Universal Asynchronous Receiver-Transmitter
import time

ldr = ADC(26)                 
led = Pin(15, Pin.OUT)      
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))     # DFPlayer Mini
# tx = transmit ; rx  = receive

# ADC.read_u16() 
dark = 4500                # when its dark 

ledtime = 2 * 60 * 1000      # 2 minutes


def df_command(cmd, param1=0, param2=0):
# Send a command packet to the DFPlayer Mini.
    packet = bytearray(10)                  # this creates space for 10 bytes; [00] [00] [00] [00] [00] [00] [00] [00] [00] [00]
    packet[0] = 0x7E                        # command packet starts here
    packet[1] = 0xFF                        # protocol
    packet[2] = 0x06                        # length of the command information that follows according to its protocol
    packet[3] = cmd                         # command => different command numbers mean different things
                                            # 0x03 = play track; 0x06 = set volume
    packet[4] = 0x00                        # feedback
    packet[5] = param1
    packet[6] = param2
    checksum = (0 - sum(packet[1:7])) & 0xFFFF      #  checks whether the command is correct or was corrupted during transmission
    packet[7] = (checksum >> 8) & 0xFF
    packet[8] = checksum & 0xFF
    packet[9] = 0xEF
    uart.write(packet)


def play_track(number):
    df_command(0x03, 0, number)      # plays 000<number>.mp3


def set_volume(level):
    df_command(0x06, 0, level)       # 0 =mute ; 30 = max


led.value(0)           # intially LED off
time.sleep(2)          # give the DFPlayer a moment to boot
set_volume(20)

light_was_on = True
led_active = False
led_start = 0


while True:
    level = ldr.read_u16()
    print(level)  

    is_dark = level < dark

    # Trigger only on the transiting from light to  dark
    if is_dark and light_was_on:
        led.value(1)
        play_track(1)           # plays 0001.mp3
        #time.sleep(2 * 60)     # cannot detect if some turn on the light after turning ti off
        #led.value(0)           
        led_active = True
        led_start = time.ticks_ms()

    light_was_on = not is_dark

    # Turn the LED off after 2 minutes
    if led_active and time.ticks_diff(time.ticks_ms(), led_start) >= ledtime:
        led.value(0)
        led_active = False

    time.sleep(2) 
