import numpy as np


def exhaustiveSearch(search_radius_k, macroblock_size, this_block, reference_frame, x, y):
    best_match = None
    min_error = 1e10 # a very big number
    best_dx = 0
    best_dy = 0
    height = reference_frame.shape[0]
    width = reference_frame.shape[1]
    
    # iterate over the search area
    for dy in range(-search_radius_k, search_radius_k + 1):
        for dx in range(-search_radius_k, search_radius_k + 1):
            # try new position
            ref_x = x + dx
            ref_y = y + dy
            
            # ensure that the reference block is within the frame boundaries (for the edges)
            if 0 <= ref_x and ref_x < width - macroblock_size:
                if 0 <= ref_y and ref_y < height - macroblock_size:
                    # extract macroblock from reference frame
                    ref_block = reference_frame[ref_y:ref_y + macroblock_size, ref_x:ref_x + macroblock_size]
                    error = np.sum((this_block - ref_block) ** 2)  # SSD
                        
                    # check if current error is minimized
                    if error < min_error:
                        min_error = error
                        best_match = ref_block
                        best_dx, best_dy = dx, dy
        
    return best_match, best_dx, best_dy

# takes search type as an argument 'exhaustive' or 'logarithmic'
def motionCompensation(search_radius_k, macroblock_size, this_frame, reference_frame, search):
    height = reference_frame.shape[0]
    width = reference_frame.shape[1]
    colors = reference_frame.shape[2]

    motion_vectors = np.zeros((height // macroblock_size, width // macroblock_size, 2), dtype=int) # populate the frame with 0s so then we can just update the location
    errors = np.zeros_like(this_frame, dtype=np.int32) # populate the frame with 0s so then we can just update the location
    
    # iterate over macroblocks in current frame
    for y in range(0, height, macroblock_size):
        for x in range(0, width, macroblock_size):
            for color in range(colors):  # process each color

                this_block = this_frame[y:y + macroblock_size, x:x + macroblock_size, color]
                
                # check search type
                if search == 'exhaustive':
                    # perform exhaustive search to find best match in reference frame for this specific color
                    # reference_frame[:, :, color] to access the entire image but one color at a time
                    best_match, dx, dy = exhaustiveSearch(search_radius_k, macroblock_size, this_block, reference_frame[:, :, color], x, y)
                elif search == 'logarithmic':
                    # perform logarithmic search to find best match in reference frame for this specific color
                    # reference_frame[:, :, color] to access the entire image but one color at a time
                    best_match, dx, dy = logarithmicSearch(search_radius_k, macroblock_size, this_block, reference_frame[:, :, color], x, y)
                    
                # update errors
                errors[y:y + macroblock_size, x:x + macroblock_size, color] = this_block - best_match
                motion_vectors[y // macroblock_size, x // macroblock_size] = [dx, dy]

    return motion_vectors, errors

def logarithmicSearch(search_radius_k, macroblock_size, this_block, reference_frame, x, y):
    best_match = None
    min_error = 1e10  # a very big number
    best_dx = 0
    best_dy = 0
    height = reference_frame.shape[0]
    width = reference_frame.shape[1]
    
    step = search_radius_k
    while step >= 1:
        
        # search in 8 position (2 vertical, 2 diagonal, 2 horizontgal)
        for dx, dy in [(0, 0), (step, 0), (-step, 0), (0, step), (0, -step), (step, step), (step, -step), (-step, step), (-step, -step)]:
            ref_x = x + dx
            ref_y = y + dy
            
            # ensure that the reference block is within the frame boundaries (for the edges)
            if 0 <= ref_x and ref_x < width - macroblock_size:
                if 0 <= ref_y and ref_y < height - macroblock_size:
                    # extract macroblock from reference frame (for one color)
                    ref_block = reference_frame[ref_y:ref_y + macroblock_size, ref_x:ref_x + macroblock_size]
                    error = np.sum((this_block - ref_block) ** 2) # SSD
                    
                    # check if error minimized
                    if error < min_error:
                        min_error = error
                        best_match = ref_block
                        best_dx, best_dy = dx, dy
            
        # half step
        step = step // 2
    
    return best_match, best_dx, best_dy
