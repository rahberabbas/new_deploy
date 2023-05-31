import pyotp

def generate_otp():
    totp = pyotp.TOTP('RLKLJMEXGZ7XULP5SJLWJY5ITOHW2TYV', digits=6, interval=300)
    otp = totp.now()
    return otp