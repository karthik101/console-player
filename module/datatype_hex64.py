# #################################################
# Data Type: hex64
# use like any normal integer.
# when converting to str or unicode object the format is:
#   0x00000000_00000000
# * casting to an int returns a 32bit number
# * casting to long retunrns the full 64bit value
# * underscores in string representation are optional

import ctypes

class hex64(ctypes.c_ulonglong):

    def __init__(self,lower,upper=0):
        """
            USE:
            hex64(2)       # returns 00000000_00000002
            hex64(2,4)     # returns 00000004_00000002
            hex64( hex64 ) # returns a copy of hex64
            lower can take any integer data type, byte, int, long, long long
            lower can also be a string with format:
                0x00000000_00000000
                
            if upper is non zero, its value is logical-ORed into the upper
                32 bit position of the unsigned 64 bit long long
        """
        if   isinstance(lower, hex64):
            lower = lower.value
        elif isinstance(lower, basestring):
            lower = lower[2:]
            lower = lower.replace('_','')
            upper = long(lower[:-8],16)
            lower = long(lower[-8:],16)

        super(hex64,self).__init__(lower);

        self.value = lower | (upper<<32)

    def __repr__(self):
        s1 = "0x%08X"%ctypes.c_ulong(self.value>>32).value
        s2 = "0x%08X"%ctypes.c_ulong(self.value    ).value
        return "hex64(%s,%s)"%(s2,s1)
    def __str__(self):
        s1 = "%08X"%ctypes.c_ulong(self.value>>32).value
        s2 = "%08X"%ctypes.c_ulong(self.value    ).value
        return "0x%s_%s"%(s1,s2)
    def __unicode__(self):
        s1 = u"%08X"%ctypes.c_ulong(self.value>>32).value
        s2 = u"%08X"%ctypes.c_ulong(self.value    ).value
        return u"0x%s_%s"%(s1,s2)
    def __int__(self):
        return int(self.value&0x00000000FFFFFFFFL)
    def __long__(self):
        return long(self.value)

    def __eq__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __EQ__ HEX64. FOUND %s"%(type(b))

        return self.value == b.value
    def __ne__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __NE__ HEX64. FOUND %s"%(type(b))

        return self.value != b.value
    def __lt__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __LT__ HEX64. FOUND %s"%(type(b))

        return self.value < b.value
    def __le__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __LE__ HEX64. FOUND %s"%(type(b))

        return self.value <= b.value
    def __gt__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __GT__ HEX64. FOUND %s"%(type(b))

        return self.value > b.value
    def __ge__(self,b):
        assert type(b) == hex64,\
            "\n*** ERROR INCOMPATABLE TYPES FOR COMPARE __GE__ HEX64. FOUND %s"%(type(b))

        return self.value >= b.value

    def truth(self):
        return self.value > 0

    def __add__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value+b)
    def __iadd__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value += b
        return self
    def __sub__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value-b)
    def __isub__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value -= b
        return self
    def __mul__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value*b)
    def __imul__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value *= b
        return self
    def __div__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value/b)
    def __idiv__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value /= b
        return self
    def __mod__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value%b)
    def __imod__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value %= b
        return self
    def __pow__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value**b)
    def __ipow__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value **= b
        return self

    def __rshift__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value>>b)
    def __irshift__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value >>= b
        return self
    def __lshift__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value<<b)
    def __ilshift__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value <<= b
        return self
    def __or__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value|b)
    def __ior__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value |= b
        return self
    def __and__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value&b)
    def __iand__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value &= b
        return self
    def __xor__(self,b):
        if type(b) == hex64:
            b = b.value
        return hex64(self.value^b)
    def __ixor__(self,b):
        if type(b) == hex64:
            b = b.value
        self.value ^= b
        return self
    def __inv__(self):
        return hex64(~self.value)
    __invert__ = __inv__
     
     

"""
    old version of hex daya type
class hex(int):
    \"""
        Sublcass pythons integer object
        to print as a hexadecimal number
        the function len() returns a hex
        number that is count characters long
        # use:
        # hex(-4).len(4) # prints 0xFFFC
    \"""
    def len(self,value):
        if value > 8: value = 8;
        if value < 1: value = 8;
        return "0x"+("%08X"%(self&0xFFFFFFFF))[-value:]
    def __repr__(self):
        return "hex(0x%08X)"%self
    def __str__(self):
        return "0x%X"%(self&0xFFFFFFFF)
    def __unicode__(self):
        return u"0x%X"%(self&0xFFFFFFFF)
"""
     