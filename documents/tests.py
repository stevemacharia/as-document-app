# from django.test import TestCase
#
# # Create your tests here.
# import uuid
#
# # make a random UUID
# print (uuid.uuid4())
# # UUID('bd65600d-8669-4903-8a14-af88203add38')
#
# # Convert a UUID to a string of hex digits in standard form
# str(uuid.uuid4())
# # 'f50ec0b7-f960-400d-91f0-c42a6d44e3d0'


import qrcode
img = qrcode.make('Some data here')
type(img)  # qrcode.image.pil.PilImage
img.save("some_file.png")