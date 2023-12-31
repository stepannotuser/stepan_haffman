from logging import root
from queue import PriorityQueue
import struct
import filecmp

class Node:
    def __init__(self, symbol=None, frequency=0, left=None, right=None):
        self.symbol = symbol
        self.frequency = frequency
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.frequency < other.frequency

def generate_dictionary(file):
    symbols = {}
    for symbol in file:
        if symbol in symbols:
            symbols[symbol] += 1
        else:
            symbols[symbol] = 1

    priority_queue = PriorityQueue()
    for symbol, frequency in symbols.items():
        node = Node(symbol, frequency)
        priority_queue.put(node)

    while priority_queue.qsize() > 1:
        left_node = priority_queue.get()
        right_node = priority_queue.get()
        combined_frequency = left_node.frequency + right_node.frequency
        parent_node = Node(frequency=combined_frequency, left=left_node, right=right_node)
        priority_queue.put(parent_node)

    root_node = priority_queue.get()
    return root_node

def build_huffman_codes(node, current_code=""):
    huffman_codes = {}
    if node.symbol:
        huffman_codes[node.symbol] = current_code
    if node.left:
        huffman_codes.update(build_huffman_codes(node.left, current_code + '0'))
    if node.right:
        huffman_codes.update(build_huffman_codes(node.right, current_code + '1'))
    return huffman_codes

def read_input(filename):
    code_txt = open(filename, "rb")   
    temp = code_txt.read()
    code_txt.close()
    return temp

def encode_text(input_text, huffman_codes):
    encoded_text = ""
    for symbol in input_text:
        encoded_text += huffman_codes[symbol]
    return encoded_text

def decode_text(encoded_text, huffman_codes):
    decoded_text = ""
    current_code = ""

    for bit in encoded_text:
        current_code += bit
        for byte, code in huffman_codes.items():
            if code == current_code:
                decoded_text += byte.decode('latin-1')  
                current_code = ""
                break

    return decoded_text

def save_data(h_cods, en_text, padding):
    encoded_file = open("encoded", "wb")
    codes_len = struct.pack('>H', len(h_cods))
    padding = struct.pack('>H', padding)
  
    encoded_file.write(codes_len)
    encoded_file.write(padding)
    
    codes_str = b""
    for byte, code in h_cods.items():
        codes_str += struct.pack("B", byte)
        codes_str += struct.pack("B", len(code))
        int_code = int(code, 2)
        codes_str += struct.pack(">I", int_code)
    
    encoded_file.write(codes_str)   
    
    encoded_bytes = bytes(int(en_text[i:i+8], 2) for i in range(0, len(en_text), 8))
    encoded_file.write(encoded_bytes)
    encoded_file.close()

def load_data(filename):
    huffman_codes = {}
    encoded_text = ""
       
    with open(filename, "rb") as file:
        codes_len = struct.unpack('>H', file.read(2))[0]
        padding = struct.unpack('>H', file.read(2))[0]

        for _ in range(codes_len):
            byte = file.read(1)
            code_len = struct.unpack("B", file.read(1))[0]
            int_code = struct.unpack(">I", file.read(4))[0]
            code = bin(int_code)[2:].rjust(code_len, '0')
            huffman_codes[byte] = code

        data_bits = file.read()
        for byte in data_bits:
            encoded_text += bin(byte)[2:].rjust(8, '0')

    return huffman_codes, encoded_text, padding

def save_decoded_text(decoded_text, filename):
    with open(filename, "wb") as file:
        file.write(decoded_text.encode('latin-1'))  


def main():
    in_text = read_input("input.txt")

    huffman_tree = generate_dictionary(in_text)
    huffman_codes = build_huffman_codes(huffman_tree)
    encoded_text = encode_text(in_text, huffman_codes)
    
    padding = 8 - len(encoded_text) % 8

    encoded_text += '0' * padding
    save_data(huffman_codes, encoded_text, padding)

    
    loaded_huffman_codes, loaded_encoded_text, load_padding  = load_data("encoded")   

    loaded_encoded_text = loaded_encoded_text[:-load_padding]
    decoded_text = decode_text(loaded_encoded_text, loaded_huffman_codes)
    
    save_decoded_text(decoded_text, "output.txt")
    
    print("input.txt == output.txt?")
    print(filecmp.cmp("input.txt", "output.txt", shallow=True))


if __name__ == "__main__":
    main()
