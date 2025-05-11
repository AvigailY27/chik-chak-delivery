from ctypes import *

mylib = cdll.LoadLibrary("./libmydemo.so")

@CFUNCTYPE(None, c_int)
def print_done(n):
    print(f"[Python] waited {n} seconds")

mylib.call_some_threads(print_done)