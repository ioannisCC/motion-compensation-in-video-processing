import heapq
from collections import defaultdict
import pickle

class Node:
    def __init__(self, data, freq):
        self.data = data
        self.freq = freq
        self.left = None
        self.right = None

    # defines how instances of the Node class will be compared
    def __lt__(self, other):
        return self.freq < other.freq

# global variable for huffman codes
codes = {}

def calcFreq(dataset):
    freq = defaultdict(int)
    for num in dataset:
        freq[num] += 1
    return freq

def buildHuffmanTree(freq):
    minHeap = [Node(data, freq) for data, freq in freq.items()]
    heapq.heapify(minHeap)

    while len(minHeap) > 1:
        left = heapq.heappop(minHeap)
        right = heapq.heappop(minHeap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(minHeap, merged)
    
    return heapq.heappop(minHeap)

def generateCodes(root, current_code=""):
    if root is None:
        return
    
    if root.data is not None:
        codes[root.data] = current_code
    
    generateCodes(root.left, current_code + "0")
    generateCodes(root.right, current_code + "1")

def encode(dataset):
    encoded_string = ""
    for num in dataset:
        encoded_string += codes[num]
    return encoded_string

# ensure that the string is multiply of 8
def padEncodedString(encoded_string):
    extra_padding = 8 - len(encoded_string) % 8
    for i in range(extra_padding):
        encoded_string += "0"
    
    padded_info = "{0:08b}".format(extra_padding)
    encoded_string = padded_info + encoded_string
    return encoded_string

def getByteArray(padded_encoded_string):
    if len(padded_encoded_string) % 8 != 0:
        print("Encoded string not padded properly")
        exit(0)
    
    byte_array = bytearray()
    for i in range(0, len(padded_encoded_string), 8):
        byte = padded_encoded_string[i:i+8]
        byte_array.append(int(byte, 2))
    return byte_array

def removePadding(padded_encoded_string):
    padded_info = padded_encoded_string[:8]
    extra_padding = int(padded_info, 2)
    
    padded_encoded_string = padded_encoded_string[8:] 
    encoded_string = padded_encoded_string[:-1*extra_padding]
    
    return encoded_string

def decode_file(codes, encoded_string):
    decoded_data = []
    current_code = ""
    
    for bit in encoded_string:
        current_code += bit
        for key, value in codes.items():
            if value == current_code:
                decoded_data.append(key)
                current_code = ""
                break
    
    return decoded_data

def writeHuffmanCodes(codes, file):
    with open(file, 'wb') as f:
        pickle.dump(codes, f)

def readHuffmanCodes(file):
    with open(file, 'rb') as f:
        codes_list = pickle.load(f)
    return codes_list
