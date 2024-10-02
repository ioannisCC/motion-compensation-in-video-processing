from huffman_bitstream import *
import cv2
import numpy as np


print('The encoding of the video has started')


capture = cv2.VideoCapture('../videos/seafood_1280p.mp4')

if not capture.isOpened():
    print("Error: Could not open the input video file.")
    exit()

# get first frame
ret = False
while ret == False:
    ret, first_frame = capture.read()
    first_frame_rgb = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGB) # make it rgb

# set codec
codec = cv2.VideoWriter_fourcc(*'XVID')

# get frames per second
fps = capture.get(cv2.CAP_PROP_FPS)
# get frame size
frame_size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
# true if the video is colored
isColor = True

# set the output for the differences frames
difference_output = cv2.VideoWriter('../videos/differences_i.avi', codec, fps, frame_size, isColor)
# same for the full video
output = cv2.VideoWriter('../videos/encoded_i.avi', codec, fps, frame_size, isColor)
if not output.isOpened():
    print("Error: Could not create the output video file.")
    capture.release()
    exit()

frame_idx = 0 
previous_frame = None
codes_dict = {}

# open a binary file to store bitstream of encoded frames
uncompressed_bitstream = open('../binary_files/uncompressed_frames.bin', 'wb')
bitstream_file = open('../binary_files/encoded_frames.bin', 'wb')

while capture.isOpened():

    ret, this_frame = capture.read()
    if not ret:
        break

    # make it rgb
    this_frame = cv2.cvtColor(this_frame, cv2.COLOR_BGR2RGB)

    # copy this frame to write it uncompressed to a binary file
    this_frame_uncompressed = this_frame.copy()

    # convert to 1D
    one_d_list_uncompressed = list(this_frame.flat)

    # convert to binary string
    binary_string_list = []
    for x in one_d_list_uncompressed:
        binary_string_list.append(format(x, '08b'))
    binary_string = ''.join(binary_string_list)

    # pad the encoded frame
    uncompressed_padded_frame = padEncodedString(binary_string)
    
    # convert to byte array
    byte_uncompressed_frame_array = getByteArray(uncompressed_padded_frame)

    # write bytes to binary file
    # write the length of the encoded data followed by the data itself
    uncompressed_bitstream.write(len(byte_uncompressed_frame_array).to_bytes(4, byteorder='big'))
    uncompressed_bitstream.write(byte_uncompressed_frame_array)

    # check every 12 frames
    if frame_idx % 12 != 0:
        # if it is a P frame then encode the difference

        # difference of frames
        difference_error = this_frame - previous_frame # 3d array

        # write the difference frame to the output
        difference_output.write(cv2.cvtColor(difference_error.astype(np.uint8), cv2.COLOR_RGB2BGR)) # astype() to make sure its a integer
        output.write(cv2.cvtColor(difference_error.astype(np.uint8), cv2.COLOR_RGB2BGR))
        one_d_list = list(difference_error.flat) # 1D list
  
    else:
        # if it is an I frame then directly encode it
        output.write(cv2.cvtColor(this_frame, cv2.COLOR_RGB2BGR))

        one_d_list = list(this_frame.flat)

    # huffman encoding
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
    bitstream_file.write(len(byte_frame_array).to_bytes(4, byteorder='big'))
    bitstream_file.write(byte_frame_array)

    codes_dict[frame_idx] = codes.copy()

    # add encoded to output   
    previous_frame = this_frame.copy()
    frame_idx += 1
    codes.clear()
    minHeap.clear()

writeHuffmanCodes(codes_dict, '../binary_files/huffman_codes.pkl')

output.release()
difference_output.release()
capture.release()
bitstream_file.close()
uncompressed_bitstream.close()


print('The encoding of the video has terminated')
