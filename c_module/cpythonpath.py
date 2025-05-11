import ctypes
import numpy as np
import platform
print(platform.architecture())

# טען את הספרייה
lib = ctypes.CDLL(r"C:\Users\WIN 11\PycharmProjects\pythonProjectyolo\delivery-form\delivery-form\c_module\path.dll")
# הגדר סוגים
lib.reorder_addresses.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int]
lib.reorder_addresses.restype = None

# יצירת מערך של קואורדינטות (lat, lon)
addresses = [(32.05, 34.77), (32.10, 34.78), (32.09, 34.75)]
flat = [item for coord in addresses for item in coord]
array = (ctypes.c_double * len(flat))(*flat)

# שלח לקוד C
lib.reorder_addresses(array, len(flat))
