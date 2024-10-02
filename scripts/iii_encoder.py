from huffman_bitstream import *
from motion_compensation import *
import cv2
import numpy as np


print('The encoding of the video has started')


capture = cv2.VideoCapture('../videos/seafood_1280p.mp4')
if not capture.isOpened():
    print("Error: Could not open the input video file.")
    exit()

# set codec
codec = cv2.VideoWriter_fourcc(*'XVID')

# get frames per second
fps = capture.get(cv2.CAP_PROP_FPS)
# get frame size
frame_size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
# true if the video is colored
isColor = True

# set the output for the differences frames
differences_output = cv2.VideoWriter('../videos/differences_iii.avi', codec, fps, frame_size, isColor)
# same for the full video
output = cv2.VideoWriter('../videos/encoded_iii.avi', codec, fps, frame_size, isColor)
if not output.isOpened():
    print("Error: Could not creb ate the output video file.")
    capture.release()
    exit()

frame_idx = 0 
reference_frame = None
macroblock_size = 16
search_radius_k = 8
motion_vectors_codes_dict = {}
error_images_dict = {}

# open a binary file to store bitstream of encoded frames
errors_bitstream_file = open('../binary_files/error_frames_log.bin', 'wb')
motion_bitstream_file = open('../binary_files/motion_vectors_log.bin', 'wb')

while capture.isOpened():

    ret, reference_frame = capture.read()
    if not ret:
        break
    
    # make it rgb
    reference_frame = cv2.cvtColor(reference_frame, cv2.COLOR_BGR2RGB)

    # check every 12 frames 
    if frame_idx % 12 != 0:
        # if it is a P frame then perform exhaustive search for motion compensation

        motion_vectors, difference_error = motionCompensation(search_radius_k, macroblock_size, reference_frame, previous_frame, 'logarithmic')
        differences_output.write(cv2.cvtColor(difference_error.astype(np.uint8), cv2.COLOR_BGR2RGB))

        # show motion vectors
        for y in range(len(motion_vectors)):
            for x in range(len(motion_vectors[y])):
                dx, dy = motion_vectors[y][x]
                start_point = (x * macroblock_size, y * macroblock_size)
                end_point = (x * macroblock_size + dx, y * macroblock_size + dy)
                color = (0, 255, 0) # RGB
                thickness = 1
                tip_length = 0.2
                cv2.arrowedLine(previous_frame, start_point, end_point, color, thickness, tipLength=tip_length)

        output.write(cv2.cvtColor(previous_frame, cv2.COLOR_BGR2RGB))
        motion_vectors_np = np.array(motion_vectors)
        one_d_list = motion_vectors_np.flatten()

        # huffman encoding of motion vectors
        minHeap = []
        encoded_frame = ""
        frequencies = calcFreq(one_d_list)
        root = buildHuffmanTree(frequencies)
        generateCodes(root)

        # encode the frame
        encoded_frame = encode(one_d_list)

        # pad the encoded frame
        padded_encoded_frame = padEncodedString(encoded_frame)
        
        # convert to byte array
        byte_frame_array = getByteArray(padded_encoded_frame)

        # write bytes to binary file
        # write the length of the encoded data followed by the data itself
        motion_bitstream_file.write(len(byte_frame_array).to_bytes(4, byteorder='big'))
        motion_bitstream_file.write(byte_frame_array)

        motion_vectors_codes_dict[frame_idx] = codes.copy()
        codes.clear()
        minHeap.clear()

        # flatten error image
        difference_error_np = np.array(difference_error)
        one_d_list = difference_error_np.flatten()
  
    else:
        # if it is an I frame then directly encode it
        output.write(cv2.cvtColor(reference_frame, cv2.COLOR_BGR2RGB))

        reference_frame_np = np.array(reference_frame)
        one_d_list = reference_frame_np.flatten()

    minHeap = []
    encoded_frame = ""
    frequencies = calcFreq(one_d_list)
    root = buildHuffmanTree(frequencies)
    generateCodes(root)

    # encode the frame
    encoded_frame = encode(one_d_list)

    # pad the encoded frame
    padded_encoded_frame = padEncodedString(encoded_frame)
    
    # convert to byte array
    byte_frame_array = getByteArray(padded_encoded_frame)

    # write bytes to binary file
    # write the length of the encoded data followed by the data itself
    errors_bitstream_file.write(len(byte_frame_array).to_bytes(4, byteorder='big'))
    errors_bitstream_file.write(byte_frame_array)

    error_images_dict[frame_idx] = codes.copy()

    # add encoded to output   
    previous_frame = reference_frame.copy()
    frame_idx += 1
    codes.clear()
    minHeap.clear()


writeHuffmanCodes(motion_vectors_codes_dict, '../binary_files/motion_vectors_codes_log.pkl')
writeHuffmanCodes(error_images_dict, '../binary_files/error_images_codes_log.pkl')

output.release()
differences_output.release()
capture.release()
errors_bitstream_file.close()
motion_bitstream_file.close()


print('The encoding of the video has terminated')