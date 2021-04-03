# Author: JuledZ
# Command Help: python main.py *image/video* *path to file*
from utils import video_main, image_main
import sys

arguments = sys.argv
input_type = arguments[1]
file_path = arguments[2]

if input_type == "image":
	print("Image selected")
	output = image_main(file_path)
	print("Image colorized ", output)
elif input_type == "video":
	print("Video selected")
	video_main(file_path)
