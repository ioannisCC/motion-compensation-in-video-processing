from huffman_bitstream import *
import cv2
import numpy as np


print('The decoding of the video has started')


# open bitstream file
with open('../binary_files/encoded_frames.bin', 'rb') as bitstream_file:

    capture = cv2.VideoCapture('../videos/encoded_i.avi')
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

    # set the output
    output = cv2.VideoWriter('../videos/decoded_i.avi', codec, fps, frame_size, isColor)
    if not output.isOpened():
        print("Error: Could not create the output video file.")
        capture.release()
        exit()

    frame_idx = 0
    previous_frame = None
    codes_dict = readHuffmanCodes('../binary_files/huffman_codes.pkl')

    while True:

        # read the length of the batch
        length_bytes = bitstream_file.read(4)
        # check end of file
        if not length_bytes:
            break
        length = int.from_bytes(length_bytes, byteorder='big')

        # read the encoded bitstream of the given length
        encoded_frame = bitstream_file.read(length)
        if not encoded_frame:
            break

        # convert bitstream bytes to binary string
        encoded_bitstream = ''.join(format(byte, '08b') for byte in encoded_frame)

        # remove padding from bitstream
        unpadded_encoded_string = removePadding(encoded_bitstream)

        # take the code of this frame
        codes = codes_dict[frame_idx]

        decoded_frame = decode_file(codes, unpadded_encoded_string)
        
        decoded_frame = np.array(decoded_frame).reshape((720, 1280, 3)) # reshape to 3 dimensions

        # check every 12 frames
        if frame_idx % 12 != 0:
            # if it is a P frame then decode the difference and add it to the previous frame
        
            this_frame = previous_frame + decoded_frame

        else:
            # if it is an I frame then directly decode it

            this_frame = decoded_frame
        
        decoded_frame_bgr = cv2.cvtColor(this_frame, cv2.COLOR_RGB2BGR)
        
        # add decoded to output
        output.write(decoded_frame_bgr)
        codes.clear()
        previous_frame = this_frame.copy()
        frame_idx += 1

    output.release()
    capture.release()
    bitstream_file.close()


print('The decoding of the video has terminated')
