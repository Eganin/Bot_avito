import pyautogui as pg
import time


def main():
    USERNAME = 'ZFe2JAVozpLZdkEEtK6z7ca9'
    PASSWORD = 'vRMUkaIGQLQa7UoatfTtjNLg'
    pg.moveTo(57, 336, 0.5)
    pg.click()
    pg.moveTo(709, 127, 0.5)
    pg.click()
    pg.typewrite('cd ~/vpn', 0.5)
    pg.typewrite(['enter'], 0.5)
    pg.moveTo(667, 143)
    pg.click()
    pg.typewrite('sudo openvpn us-free-01.protonvpn.com.udp.ovpn')
    pg.typewrite(['enter'])
    pg.moveTo(353, 174)
    pg.typewrite('Zaharin0479')
    pg.typewrite(['enter'])
    time.sleep(5)
    pg.moveTo(313, 237)
    pg.typewrite(USERNAME)
    pg.typewrite(['enter'])
    pg.moveTo(535, 258)
    pg.typewrite(PASSWORD)
    pg.typewrite(['enter'])


main()
