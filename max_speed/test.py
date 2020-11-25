import sys
import os

old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')
print('hey')
sys.stdout.close()
sys.stdout = old_stdout
print('hi')

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__

blockPrint()
print('yo')
enablePrint()
print('sup')

for i in range(1,5):
    print('yes yes yes')
    blockPrint()
    print('no no no')
    enablePrint()
    print('oh yeah')