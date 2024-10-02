from huffman_bitstream import *
from motion_compensation import *
import cv2
import numpy as np


print('The decoding of the video has started')


motion_vectors_codes_dict = readHuffmanCodes('../binary_files/motion_vectors_codes.pkl')
error_images_dict = readHuffmanCodes('../binary_files/error_images_codes.pkl')

# open bitstream file
with open('../binary_files/error_frames.bin', 'rb') as bitstream_file_frames:
    with open('../binary_files/motion_vectors.bin', 'rb') as bitstream_file_motion_vectors:

        capture = cv2.VideoCapture('../videos/encoded_ii.avi')
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
        output = cv2.VideoWriter('../videos/decoded_ii.avi', codec, fps, frame_size, isColor)
        if not output.isOpened():
            print("Error: Could not create the output video file.")
            capture.release()
            exit()

        frame_idx = 0
        previous_frame = None
        macroblock_size = 16
        search_radius_k = 8

        while True:
            
            # decode error frame

            # read the length of the batch for the error frames
            length_bytes = bitstream_file_frames.read(4)
            # check end of file
            if not length_bytes:
                break
            length = int.from_bytes(length_bytes, byteorder='big')

            # read the encoded bitstream of the given length
            encoded_frame = bitstream_file_frames.read(length)
            if not encoded_frame:
                break

            # convert bitstream bytes to binary string
            encoded_bitstream = ''.join(format(byte, '08b') for byte in encoded_frame)

            # remove padding from bitstream
            unpadded_encoded_string = removePadding(encoded_bitstream)

            # take the code of this frame
            error_codes = error_images_dict[frame_idx]

            decoded_frame = decode_file(error_codes, unpadded_encoded_string)
            
            this_frame = np.array(decoded_frame).reshape((720, 1280, 3)) # reshape to 3 dimensions

            # check every 12 frames
            if frame_idx % 12 != 0:
                # if it is a P frame then reconstruct the frame from the motion vectors

                # decode motion vectors

                # read the length of the batch for the error frames
                length_bytes = bitstream_file_motion_vectors.read(4)
                # check end of file
                if not length_bytes:
                    break
                length = int.from_bytes(length_bytes, byteorder='big')

                # read the encoded bitstream of the given length
                encoded_motion_vectors = bitstream_file_motion_vectors.read(length)
                if not encoded_motion_vectors:
                    break

                # convert bitstream bytes to binary string
                encoded_bitstream = ''.join(format(byte, '08b') for byte in encoded_motion_vectors)

                # remove padding from bitstream
                unpadded_encoded_string = removePadding(encoded_bitstream)

                # take the code of this frame
                motion_vectors_codes = motion_vectors_codes_dict[frame_idx]

                decoded_motion_vector = decode_file(motion_vectors_codes, unpadded_encoded_string)

                motion_vectors = np.array(decoded_motion_vector).reshape((this_frame.shape[0] // macroblock_size, this_frame.shape[1] // macroblock_size, 2)) # reshape to 2 dimensions

                reconstructed_frame = np.zeros_like(previous_frame, dtype=np.uint8)

                # apply the motion vectors to reconstruct this frame
                for y in range(len(motion_vectors)):
                    for x in range(len(motion_vectors[y])):
                        dx, dy = motion_vectors[y][x]
                        start_point = (x * macroblock_size, y * macroblock_size)
                        end_point = (start_point[0] + dx, start_point[1] + dy)
                        
                        # ensure the end point is within the frame boundaries
                        end_point_x = min(max(end_point[0], 0), previous_frame.shape[1] - macroblock_size)
                        end_point_y = min(max(end_point[1], 0), previous_frame.shape[0] - macroblock_size)

                        # ensure the block does not go out of frame boundaries
                        block_width = min(macroblock_size, previous_frame.shape[1] - end_point_x)
                        block_height = min(macroblock_size, previous_frame.shape[0] - end_point_y)

                        for color in range(previous_frame.shape[2]):
                            reconstructed_frame[y * macroblock_size : y * macroblock_size + block_height, 
                                x * macroblock_size : x * macroblock_size + block_width, color] = previous_frame[
                                                                                              end_point_y:end_point_y + block_height, 
                                                                                              end_point_x:end_point_x + block_width, color]

                # add the error image
                reconstructed_frame = reconstructed_frame + this_frame

            else:
                # if it is an I frame then directly write it to output
                
                reconstructed_frame = this_frame.copy()
            
            reconstructed_frame_bgr = cv2.cvtColor(reconstructed_frame.astype(np.uint8), cv2.COLOR_RGB2BGR)
            # add decoded to output
            output.write(reconstructed_frame_bgr)
            previous_frame = reconstructed_frame_bgr.copy()
            frame_idx += 1

        output.release()
        capture.release()

bitstream_file_frames.close()
bitstream_file_motion_vectors.close()


print('The decoding of the video has terminated')