import pyautogui as pg
import time
import sys


def main():
    TOWN = 'moskva'
    ITEM = 'Xiaomi'
    pg.moveTo(53, 465, 0.5)
    pg.click()
    pg.moveTo(1839, 637, 0.5)
    pg.click()
    pg.typewrite('/start', 0.5)
    pg.typewrite(['enter'])
    pg.moveTo(1492, 636, 0.5)
    pg.click()
    time.sleep(2)
    pg.moveTo(1511, 548, 0.5)
    pg.click()
    time.sleep(2)
    pg.moveTo(1773, 496, 0.5)
    pg.click()
    time.sleep(2)
    pg.moveTo(1484, 504, 0.5)
    pg.click()
    time.sleep(6)
    pg.typewrite(TOWN)
    pg.typewrite(['enter'])
    time.sleep(2)
    pg.typewrite(ITEM)
    pg.typewrite(['enter'])
    time.sleep(2)
    pg.typewrite('-')
    pg.typewrite(['enter'])
    time.sleep(2)
    pg.typewrite('-')
    pg.typewrite(['enter'])
    time.sleep(2)
    pg.moveTo(1492, 541)
    pg.click()


def main_href():
    HREF = 'https://www.avito.ru/moskva/noutbuki?q=Xiaomi'
    pg.moveTo(53, 465, 0.5)
    pg.click()
    pg.moveTo(1839, 637, 0.5)
    pg.click()
    pg.typewrite('/start', 0.5)
    pg.typewrite(['enter'])
    pg.moveTo(1492, 636, 0.5)
    pg.click()
    time.sleep(3)
    pg.moveTo(1762, 543)
    pg.click()
    pg.typewrite(HREF)
    pg.typewrite(['enter'])
    pg.moveTo(1498, 542)
    pg.click()
    for i in range(3):
        time.sleep(2)
        pg.moveTo(1469, 550)
        pg.click()


def main_vpn():
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
