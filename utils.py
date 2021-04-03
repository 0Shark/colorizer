# Author: JuledZ
import cv2
import os
from os.path import isfile, join
import random
import string
import requests
import re
import shutil 


deepai_api_key = "*INSERT-YOUR-API-KEY-HERE*"

def rand_string(length):
	rand_str = "".join(random.choice(
				string.ascii_lowercase
				+ string.ascii_uppercase
				+ string.digits)
			for i in range(length))
	return rand_str

def get_video_length(video_path):
	cap = cv2.VideoCapture(video_path)
	length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	return length

def extract_frames(video_path, skip_frames=1):
	_, file_name = os.path.split(video_path)
	file_name_without_ext = os.path.splitext(file_name)[0]
	length = get_video_length(video_path)
	if length == 0:
		return 0
	cap = cv2.VideoCapture(video_path)
	count = 0
	video_id = rand_string(5)
	video_filename = "".join(file_name_without_ext[:6]+video_id)
	save_path = "temp/"+ video_filename
	while True:	
		try:
			fix = "".join(save_path+"/fix_frames")
			raw = "".join(save_path+"/raw_frames")
			os.makedirs(fix)
			os.makedirs(raw)    
			print("Directory created for ", save_path)
			break
		except FileExistsError:
		    print("Directory " , save_path ,  " already exists, reseting id", end='\r') 
		    video_id = rand_string(5)
		    video_filename = "".join(file_name_without_ext[:6]+video_id)
		    save_path = "temp/"+ video_filename

	save_path = "temp/"+ video_filename +"/raw_frames/"
	# test first frame
	ret,frame = cap.read()
	test_file_path = os.path.join(
  					 save_path,
					 file_name_without_ext[:6]+\
					 '{}.jpg'.format(video_id, count))

	cv2.imwrite(test_file_path, frame)
	if os.path.isfile(test_file_path):
		os.remove(test_file_path)
		count = 1
		while ret:
			ret,frame = cap.read()
			if ret and count % skip_frames == 0:
				cv2.imwrite(os.path.join(
					save_path,
					file_name_without_ext[:6]+
					'{}_{}.jpg'.format(video_id, count)
					), frame)
				count += 1
				print("Generated {}/{} frames".format(count, length), end='\r')
			else:
				count += 1
	else:
		print("Test file cannot be saved")
		return 0

	

	return video_filename, count
	cap.release()


def converge_frames(video_len, video_filename, fps):
	frame_array = []
	temp_path = 'temp/' + video_filename + '/fix_frames/'
	files = [f for f, x in zip(os.listdir(temp_path), range(video_len)) if isfile(join(temp_path, video_filename + '_' + str(x) + '.jpg'))]
	files.sort(key=lambda f: int(re. sub('\D', '', f)))
	#print(files)
	for i in range(len(files)):
		filename = temp_path + files[i]
		# reading files
		img = cv2.imread(filename)
		height, width, layers = img.shape
		size = (width,height)
		print("Proccessed {}/{} frames of video".format(i, video_len), end='\r')
		frame_array.append(img)

	output_path = 'output/' + video_filename + '.mp4' # If video output error .avi may be a good option
	out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
	for i in range(len(frame_array)):
		# writing to image array
		out.write(frame_array[i])
	out.release()
	return output_path


def colorize(video_len, video_filename):
	for x in range(1, video_len):
		raw_path = ''.join('temp/' + video_filename + '/raw_frames/'+video_filename+'_'+str(x)+'.jpg')
		r = requests.post(
		    "https://api.deepai.org/api/colorizer",
		    files={
		        'image': open(raw_path, 'rb'),
		    },
		    headers={'api-key': 'b891cd87-6737-49ea-9fb1-44009b0daa78'}
		)
		response = r.json()
		output_url = response['output_url']
		download_img = requests.get(output_url)
		fix_path = ''.join('temp/' + video_filename + '/fix_frames/'+video_filename+'_'+str(x)+'.jpg')
		proccessed_frame = open(fix_path, "wb")
		proccessed_frame.write(download_img.content)
		proccessed_frame.close()
		print("Colorized {}/{} frames".format(x, video_len), end='\r')


def clear_workspace(video_filename):
	cur_path = "".join('temp/'+video_filename)
	shutil.rmtree(cur_path)


def video_main(video):
	video = str(video)
	video.replace(" ", "_")
	# print(video)
	cur_video = cv2.VideoCapture(video)
	fps = cur_video.get(cv2.CAP_PROP_FPS)
	extraction_results = extract_frames(video, skip_frames=1)
	video_filename = extraction_results[0]
	frames_extracted = extraction_results[1]
	print("\n")
	colorize(frames_extracted, video_filename)
	print("\n")
	created_video = converge_frames(frames_extracted, video_filename, fps)
	print("Cleaning workspace for ", video_filename)
	#clear workspace
	clear_workspace(video_filename)
	print("Your video was colorized: ", created_video)


def image_main(image):
	_, file_name = os.path.split(image)
	file_name_without_ext = os.path.splitext(file_name)[0]
	image_id = rand_string(5)
	image_filename = "".join(file_name_without_ext[:6]+image_id)
	print("Uploading...")
	r = requests.post(
	    "https://api.deepai.org/api/colorizer",
	    files={
	        'image': open(image, 'rb'),
	    },
	    headers={'api-key': deepai_api_key}
	)
	response = r.json()
	output_url = response['output_url']
	download_img = requests.get(output_url)
	print("Saving...")
	fix_path = ''.join('output/' + image_filename + '.jpg')
	proccessed_frame = open(fix_path, "wb")
	proccessed_frame.write(download_img.content)
	proccessed_frame.close()
	return fix_path
