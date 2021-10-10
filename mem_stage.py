import struct
import binascii
import logging
from cpu_types import Utils


class Mem():
    """
    ws(addr, dat)
    r32(addr)
    """


    def __init__(self):
        self.memory = b'\x00'*0x4000
        self.csrs = CSregs()
    def ws(self, addr, dat):
        addr -= 0x80000000
        assert addr >=0 and addr < len(self.memory)
        self.memory = self.memory[:addr] + dat + self.memory[addr+len(dat):]

    def r32(self, addr):
        addr -= 0x80000000
        if addr < 0 or addr >= len(self.memory):
            raise Exception("mem fetch to %x failed" % addr)
        assert addr >=0 and addr < len(self.memory)
        return struct.unpack("<I", self.memory[addr:addr+4])[0]

    def load(self, g):
        g.write(b'\n'.join([binascii.hexlify(self.memory[i:i+4][::-1]) for i in range(0,len(self.memory),4)]))
        
    def reset(self):
        self.csrs.cregs =  b'\x00'*0x4000
        self.memory =  b'\x00'*0x4000

class CSregs():
    def __init__(self):
        self.modified = {}
        self.cregs =  b'\x00'*0x4000
    def __getitem__(self, key):
        addr = key << 2
        return Utils.htoi(self.cregs[addr:addr+4])
    def __setitem__(self, key, val):
        addr = key << 2
        dat = struct.pack("<I", val & 0xFFFFFFFF) 
        self.cregs = self.cregs[:addr] + dat + self.cregs[addr+len(dat):]
        self.modified[key] = dat
        logging.debug("0x%s:  %s", key, Utils.zext(Utils.htoi(dat)))
    def print_modified(self):
        for key, value in self.modified.items():
            print(f'0x{key:x}:  {Utils.zext(Utils.htoi(value)):s}')
    def __str__(self):
        s = ""
        for key, value in self.modified.items():
            s = s + f'0x{key:x}:  {Utils.zext(Utils.htoi(value)):s}\n'

        return s