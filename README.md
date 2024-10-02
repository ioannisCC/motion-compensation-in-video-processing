
**First Query**: Compression and Error Images (No Motion Compensation):

The task involved calculating and displaying the error images resulting from compressing video frames without motion compensation.
P-frames (predicted frames) are computed by taking the difference between the current frame (P) and the previous frame (P-1). The difference frame is then encoded using Huffman coding and stored in a binary file.
I-frames (intra-coded frames) are encoded independently, using Huffman coding without referencing any other frame. This ensures that I-frames can be decoded independently, while P-frames rely on previous frames for reconstruction.

**Second Query**: Motion Compensation via Exhaustive Search:

The task involved calculating motion vectors for P-frames using exhaustive search within a search radius [-k, +k].

The Sum of Squared Differences (SSD) was used to find the best match for macroblocks between frames, returning the best match and corresponding motion vectors.
	
For decoding, the inverse process was applied, reconstructing the frames using the motion vectors.

**Compression Ratios**:

Compression ratios were calculated as the ratio of uncompressed symbols (original video bits) to compressed symbols (compressed video bits).
	
The formula is: Compression Ratio = (original bitstream size) / (compressed bitstream size).
