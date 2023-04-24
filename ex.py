# # # 1. Install Pillow (Pillow will not work if you have PIL installed):
# # # python3 -m pip install --upgrade pip
# # # python3 -m pip install --upgrade Pillow
# # # python3 -m pip install Exif-python

from exif import Image
# def convert_to_decimal(degrees, minutes, seconds, direction):
#     # Calculate the decimal degrees
#     decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)

#     # Adjust for the direction (negative for south or west)
#     if direction in ['S', 'W']:
#         decimal_degrees = -decimal_degrees

#     return decimal_degrees

def convert_dms_to_decimal(degrees, minutes, seconds):
    # Calculate the decimal degrees
    decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)

    return decimal_degrees



def generate_google_maps_link(latitude, longitude):
    # Construct the Google Maps URL
    url = f'https://www.google.com/maps/search/?api=1&query={latitude},{longitude}'

    return url

img_path = '/home/falcon/Desktop/IMG1.jpg'
with open('IMG1.jpg', 'rb') as image_file:
    my_image = Image(image_file)

# print(my_image.has_exif)
latitude = my_image.gps_latitude
longitude = my_image.gps_longitude

print(latitude)
print(longitude)



latitude = convert_dms_to_decimal(*latitude)
longitude = convert_dms_to_decimal(*longitude)
print(latitude, longitude)

google_maps_link = generate_google_maps_link(latitude, longitude)
print(google_maps_link)

# import Exif
# imagename = "C:\\Users\\rajhe\\Downloads\\Plane.jpg"
# imagename = "IMG.jpg"
# exif_data = Exif.get_exif_for_file(imagename)
# exif_data = Exif.get_exif(imagename)
# print(type(exif_data))
# print(exif_data)

# print("Name: ", exif_data['FileName'])
# print("DateTime: ", exif_data['DateTime'])
# print("Make: ", exif_data['Make'])
# print("Model: ", exif_data['Model'])
# print("GPSInfo: ", exif_data['GPSInfo'])
# # print("Copyright: ", exif_data['Copyright'])
# # print("Artist: ", exif_data['Artist'])
# print("ImageHeight: ", exif_data['ImageHeight'])
# print("ImageWidth: ", exif_data['ImageWidth'])
# print("ImageFormat: ", exif_data['ImageFormat'])
# print("IsAnimated: ", exif_data['IsAnimated'])


# def decimal_coords(coords, ref):
#  decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
#  if ref == "S" or ref == "W":
#      decimal_degrees = -decimal_degrees
#  return decimal_degrees

# def image_coordinates(image_path):
#     with open(img_file, 'rb') as src:
#         img = Image(src)
#     if img.has_exif:
#         try:
#             img.gps_longitude
#             coords = (decimal_coords(img.gps_latitude,
#                       img.gps_latitude_ref),
#                       decimal_coords(img.gps_longitude,
#                       img.gps_longitude_ref))
#         except AttributeError:
#             print ('No Coordinates')
#     else:
#         print ("The Image has no EXIF information")
#     print(
#         f"Image {src.name}, OS Version:{img.get('software', 'Not Known')} ------")
#     print(f"Was taken: {img.datetime_original}, and has coordinates:{coords}")


# import os
# from PIL import Image
# from PIL.ExifTags import TAGS
# img_file = "IMG.JPG"
# image = Image.open(img_file)
# exif = {}
# for tag, value in image. _getexif() . items():
#     if tag in TAGS:
#         exif[TAGS[tag]] = value
# # print(exif)
# print(image_coordinates(img_file))
# print(type(exif))

# # print("Name: ", exif['FileName'])
# print("DateTime: ", exif['DateTime'])
# print("Make: ", exif['Make'])
# print("Model: ", exif['Model'])
# print("GPSInfo: ", exif['GPSInfo'])
# # print("Copyright: ", exif['Copyright'])
# # print("Artist: ", exif['Artist'])
# # print("ImageHeight: ", exif['ImageHeight'])
# # print("ImageWidth: ", exif['ImageWidth'])
# print("ImageFormat: ", exif['ImageFormat'])
# print("IsAnimated: ", exif['IsAnimated'])
