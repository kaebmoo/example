import pyotp
import time

totp = pyotp.TOTP('base32secret3232')

print(totp.now())

print(totp.verify(totp.now())) 

