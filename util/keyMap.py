#!/usr/bin/env python
from PyQt4 import QtCore
import win32con
#from project.dictSet import DictSet
keyMap = {
    "ALT":0x0001, 
    "NONE":0x000, 
    "CONTROL":0x0002, 
    "SHIFT":0x0004, 
    "WIN":0x0008, 
    "F1":win32con.VK_F1, 
    "F2":win32con.VK_F2, 
    "F3":win32con.VK_F3, 
    "F4":win32con.VK_F4, 
    "F5":win32con.VK_F5, 
    "F6":win32con.VK_F6, 
    "F7":win32con.VK_F7, 
    "F8":win32con.VK_F8, 
    "F9":win32con.VK_F9, 
    "F10":win32con.VK_F10, 
    "F11":win32con.VK_F11, 
    "F12":win32con.VK_F12, 
    "PRINT":win32con.VK_PRINT, 
    "A":ord("A"), 
    "B":ord("B"), 
    "C":ord("C"), 
    "D":ord("D"), 
    "E":ord("E"), 
    "F":ord("F"), 
    "G":ord("G"), 
    "H":ord("H"), 
    "I":ord("I"), 
    "J":ord("J"), 
    "K":ord("K"), 
    "L":ord("L"), 
    "M":ord("M"), 
    "N":ord("N"), 
    "O":ord("O"), 
    "P":ord("P"), 
    "Q":ord("Q"), 
    "R":ord("R"), 
    "S":ord("S"), 
    "T":ord("T"), 
    "U":ord("U"), 
    "V":ord("V"), 
    "W":ord("W"), 
    "X":ord("X"), 
    "Y":ord("Y"), 
    "Z":ord("Z"), 
    "0":QtCore.Qt.Key_0, 
    "1":QtCore.Qt.Key_1, 
    "2":QtCore.Qt.Key_2, 
    "3":QtCore.Qt.Key_3, 
    "4":QtCore.Qt.Key_4, 
    "5":QtCore.Qt.Key_5, 
    "6":QtCore.Qt.Key_6, 
    "7":QtCore.Qt.Key_7, 
    "8":QtCore.Qt.Key_8, 
    "9":QtCore.Qt.Key_9, 
    }
def getKey(key):
    '''获取键位码,用于全局快捷键注册'''
    return keyMap.get(key)
