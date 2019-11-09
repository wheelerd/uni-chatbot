#!/usr/bin/env python3
from bitstream import BitStream
from numpy import uint8, uint16
from reedsolo import RSCodec
from math import ceil, floor
from enum import IntEnum
from io import BytesIO
from PIL import Image

class QR_ECC(IntEnum):
    """ Error correction capability (ECC) levels for QR code encoding """
    L = 0 # Low
    M = 1 # Medium
    Q = 2 # Quality
    H = 3 # High (best)
    
    def asString(ecc):
        if ecc == QR_ECC.L:
            return "L"
        elif ecc == QR_ECC.M:
            return "M"
        elif ecc == QR_ECC.Q:
            return "Q"
        elif ecc == QR_ECC.H:
            return "H"
        else:
            raise Exception("Unknown QR_ECC value: {}".format(ecc))

class QR_Exception(Exception):
    """ QRCode will _ONLY_ raise these exceptions. If not, there is a bug somewhere """
    pass

class Module(IntEnum):
    """ Module values for matrices """
    Black = 0
    White = 1
    Unset = -1
    
    def flip(module):
        if module == Module.Black:
            return Module.White
        elif module == Module.White:
            return module.Black
        else:
            raise Exception("Cannot flip unset module")

class ModuleMatrix:
    """ A class for storing modules in a matrix. E.g. patterns and QR codes """
    def __init__(self, width, height):
        """ Constructor. Makes a blank matrix of the specified dimensions """
        self._width = width
        self._height = height
        self._modules = []
        
        # Gen blank matrix
        row = [ Module.Unset ] * width
        for i in range(height):
            self._modules.append(row.copy())
    
    def fromStrList(array):
        """ Factory that makes a new matrix out of a string list. B is black, W is white, spaces are unset """
        # Blank matrix
        height = len(array)
        width = len(array[0])
        matrix = ModuleMatrix(width, height)
        
        # Generate from string list
        for y in range(height):
            for x in range(width):
                modChar = array[y][x].lower()
                if modChar == ' ':
                    module = Module.Unset
                elif modChar == 'w':
                    module = Module.White
                elif modChar == 'b':
                    module = Module.Black
                else:
                    raise Exception("Unexpected character: {}".format(modChar))
                
                matrix[x, y] = module
        
        # Done
        return matrix
    
    def copy(self):
        """ Creates a new instance which is a copy of the matrix """
        matrixCopy = ModuleMatrix(self._width, self._height)
        for y in range(self._height):
            for x in range(self._width):
                matrixCopy[x, y] = self[x, y]
        
        return matrixCopy
    
    def overwrite(self, matrix):
        """ Overwrites self with the given matrix """
        self._width, self._height = matrix.getDimensions()
        for y in range(self._height):
            for x in range(self._width):
                self[x, y] = matrix[x, y]
    
    def getDimensions(self):
        """ Get matrix dimensions """
        return self._width, self._height
    
    def __getitem__(self, pos):
        """ Get module at position """
        return self._modules[pos[1]][pos[0]]
    
    def __setitem__(self, pos, module):
        """ Set module at position """
        self._modules[pos[1]][pos[0]] = module
    
    def applyPattern(self, x, y, pattern):
        """ Apply a pattern at a position. The position is the top-left corner of the pattern """
        pWidth, pHeight = pattern.getDimensions()
        for dy in range(pHeight):
            # Real Y coordinate
            ry = y + dy
            if ry >= 0 and ry < self._height:
                for dx in range(pWidth):
                    # Skip if module unset in pattern
                    thisModule = pattern[dx, dy]
                    if thisModule == Module.Unset:
                        continue
                    
                    # Real X coordinate
                    rx = x + dx
                    if rx >= 0 and rx < self._width:
                        self[rx, ry] = thisModule
    
    def applyMask(self, x, y, mask):
        """ Applies a mask pattern at a position by XORing modules instead of overwriting """
        mWidth, mHeight = mask.getDimensions()
        for dy in range(mHeight):
            # Real Y coordinate
            ry = y + dy
            if ry >= 0 and ry < self._height:
                for dx in range(mWidth):
                    # Skip if module unset in mask
                    thisModule = mask[dx, dy]
                    if thisModule == Module.Unset:
                        continue
                    
                    # Real X coordinate
                    rx = x + dx
                    if rx >= 0 and rx < self._width:
                        # Skip if module unset in matrix
                        if self[rx, ry] == Module.Unset:
                            continue
                        
                        # Flip if mask module is black
                        if thisModule == Module.Black:
                            if self[rx, ry] == Module.Black:
                                self[rx, ry] = Module.White
                            else:
                                self[rx, ry] = Module.Black
    
    def applyMaskRepeated(self, mask):
        """ Repeats a mask pattern from the top left to the bottom right """
        mWidth, mHeight = mask.getDimensions()
        for y in range(0, self._height, mHeight):
            for x in range(0, self._width, mWidth):
                # Apply mask at this position
                self.applyMask(x, y, mask)
    
    def extractUnset(self):
        """ Creates a copy of the matrix, with set modules as unset and unset modules as white """
        matrixCopy = self.copy()
        for y in range(self._height):
            for x in range(self._width):
                thisModule = self[x, y]
                if thisModule == Module.Unset:
                    thisModule = Module.White
                else:
                    thisModule = Module.Unset
                
                matrixCopy[x, y] = thisModule
        
        return matrixCopy
    
    def getPenaltyScore(self):
        """ Get the penalty score of the current matrix """
        score = 0
        
        # Find consecutive horizontal lines
        for y in range(self._height):
            length = 0
            lastModule = Module.Unset
            for x in range(self._width):
                thisModule = self[x, y]
                if thisModule == lastModule:
                    length += 1
                    if length == 5:
                        score += 3
                    elif length > 5:
                        score += 1
                else:
                    length = 1
                lastModule = thisModule
        
        # Find consecutive vertical lines
        for x in range(self._width):
            length = 0
            lastModule = Module.Unset
            for y in range(self._height):
                thisModule = self[x, y]
                if thisModule == lastModule:
                    length += 1
                    if length == 5:
                        score += 3
                    elif length > 5:
                        score += 1
                else:
                    length = 1
                lastModule = thisModule
        
        # Find 2x2 squares
        for x in range(self._width - 1):
            for y in range(self._height - 1):
                expectedModule = self[x, y]
                if expectedModule == self[x + 1, y] and expectedModule == self[x, y + 1] and expectedModule == self[x + 1, y + 1]:
                    score += 3
        
        # Find the sequence bwbbbwbwwww and wwwwbwbbbwb...
        firstSequence = [Module.Black, Module.White, Module.Black, Module.Black, Module.Black, Module.White, Module.Black, Module.White, Module.White, Module.White, Module.White]
        secondSequence = firstSequence.copy()
        secondSequence.reverse()
        def horizSequenceMatches(x, y, sequence):
            for dx in range(len(sequence)):
                if self[x + dx, y] != sequence[dx]:
                    return False
            return True
        
        def vertSequenceMatches(x, y, sequence):
            for dy in range(len(sequence)):
                if self[x, y + dy] != sequence[dy]:
                    return False
            return True
        
        # ... horizontally
        for x in range(self._width - 10):
            for y in range(self._height):
                if horizSequenceMatches(x, y, firstSequence):
                    score += 40
                if horizSequenceMatches(x, y, secondSequence):
                    score += 40
        
        # ... vertically
        for y in range(self._height - 10):
            for x in range(self._width):
                if vertSequenceMatches(x, y, firstSequence):
                    score += 40
                if vertSequenceMatches(x, y, secondSequence):
                    score += 40
        
        # Add black/white ratio penalty
        black = 0
        white = 0
        for x in range(self._width):
            for y in range(self._height):
                if self[x, y] == Module.Black:
                    black += 1
                else:
                    white += 1
        bwRatio = (black / white) * 100
        prevMulPenalty = abs(floor(bwRatio / 5) * 5 - 50) // 5
        nextMulPenalty = abs(floor((bwRatio + 5) / 5) * 5 - 50) // 5
        score += min(prevMulPenalty, nextMulPenalty) * 10
        
        return score
    
    def toImage(self):
        """ Convert matrix to image """
        image = Image.new('1', (self._width, self._height), 0)
        pixels = image.load()
        for y in range(self._height):
            for x in range(self._width):
                if self[x, y] == Module.Unset:
                    raise Exception("Unexpected unfilled module at ({}, {})".format(x, y))
                pixels[x, y] = self[x, y]
        
        return image

class QRCode(ModuleMatrix):
    """ The QR code encoder class. Only encodes in byte mode """
    
    # Version list. Contains the maximum bytes for L, M, Q, H error correction levels respectively
    # From https://www.thonky.com/qr-code-tutorial/character-capacities
    VERSION_LIST = ((17,14,11,7),(32,26,20,14),(53,42,32,24),(78,62,46,34),(106,84,60,44),(134,106,74,58),(154,122,86,64),(192,152,108,84),(230,180,130,98),(271,213,151,119),(321,251,177,137),(367,287,203,155),(425,331,241,177),(458,362,258,194),(520,412,292,220),(586,450,322,250),(644,504,364,280),(718,560,394,310),(792,624,442,338),(858,666,482,382),(929,711,509,403),(1003,779,565,439),(1091,857,611,461),(1171,911,661,511),(1273,997,715,535),(1367,1059,751,593),(1465,1125,805,625),(1528,1190,868,658),(1628,1264,908,698),(1732,1370,982,742),(1840,1452,1030,790),(1952,1538,1112,842),(2068,1628,1168,898),(2188,1722,1228,958),(2303,1809,1283,983),(2431,1911,1351,1051),(2563,1989,1423,1093),(2699,2099,1499,1139),(2809,2213,1579,1219),(2953,2331,1663,1273))
    
    # ECC block information list
    # From https://www.thonky.com/qr-code-tutorial/error-correction-table
    BLOCK_LIST = (((7,1,19),(10,1,16),(13,1,13),(17,1,9)),((10,1,34),(16,1,28),(22,1,22),(28,1,16)),((15,1,55),(26,1,44),(18,2,17),(22,2,13)),((20,1,80),(18,2,32),(26,2,24),(16,4,9)),((26,1,108),(24,2,43),(18,2,15,2,16),(22,2,11,2,12)),((18,2,68),(16,4,27),(24,4,19),(28,4,15)),((20,2,78),(18,4,31),(18,2,14,4,15),(26,4,13,1,14)),((24,2,97),(22,2,38,2,39),(22,4,18,2,19),(26,4,14,2,15)),((30,2,116),(22,3,36,2,37),(20,4,16,4,17),(24,4,12,4,13)),((18,2,68,2,69),(26,4,43,1,44),(24,6,19,2,20),(28,6,15,2,16)),((20,4,81),(30,1,50,4,51),(28,4,22,4,23),(24,3,12,8,13)),((24,2,92,2,93),(22,6,36,2,37),(26,4,20,6,21),(28,7,14,4,15)),((26,4,107),(22,8,37,1,38),(24,8,20,4,21),(22,12,11,4,12)),((30,3,115,1,116),(24,4,40,5,41),(20,11,16,5,17),(24,11,12,5,13)),((22,5,87,1,88),(24,5,41,5,42),(30,5,24,7,25),(24,11,12,7,13)),((24,5,98,1,99),(28,7,45,3,46),(24,15,19,2,20),(30,3,15,13,16)),((28,1,107,5,108),(28,10,46,1,47),(28,1,22,15,23),(28,2,14,17,15)),((30,5,120,1,121),(26,9,43,4,44),(28,17,22,1,23),(28,2,14,19,15)),((28,3,113,4,114),(26,3,44,11,45),(26,17,21,4,22),(26,9,13,16,14)),((28,3,107,5,108),(26,3,41,13,42),(30,15,24,5,25),(28,15,15,10,16)),((28,4,116,4,117),(26,17,42),(28,17,22,6,23),(30,19,16,6,17)),((28,2,111,7,112),(28,17,46),(30,7,24,16,25),(24,34,13)),((30,4,121,5,122),(28,4,47,14,48),(30,11,24,14,25),(30,16,15,14,16)),((30,6,117,4,118),(28,6,45,14,46),(30,11,24,16,25),(30,30,16,2,17)),((26,8,106,4,107),(28,8,47,13,48),(30,7,24,22,25),(30,22,15,13,16)),((28,10,114,2,115),(28,19,46,4,47),(28,28,22,6,23),(30,33,16,4,17)),((30,8,122,4,123),(28,22,45,3,46),(30,8,23,26,24),(30,12,15,28,16)),((30,3,117,10,118),(28,3,45,23,46),(30,4,24,31,25),(30,11,15,31,16)),((30,7,116,7,117),(28,21,45,7,46),(30,1,23,37,24),(30,19,15,26,16)),((30,5,115,10,116),(28,19,47,10,48),(30,15,24,25,25),(30,23,15,25,16)),((30,13,115,3,116),(28,2,46,29,47),(30,42,24,1,25),(30,23,15,28,16)),((30,17,115),(28,10,46,23,47),(30,10,24,35,25),(30,19,15,35,16)),((30,17,115,1,116),(28,14,46,21,47),(30,29,24,19,25),(30,11,15,46,16)),((30,13,115,6,116),(28,14,46,23,47),(30,44,24,7,25),(30,59,16,1,17)),((30,12,121,7,122),(28,12,47,26,48),(30,39,24,14,25),(30,22,15,41,16)),((30,6,121,14,122),(28,6,47,34,48),(30,46,24,10,25),(30,2,15,64,16)),((30,17,122,4,123),(28,29,46,14,47),(30,49,24,10,25),(30,24,15,46,16)),((30,4,122,18,123),(28,13,46,32,47),(30,48,24,14,25),(30,42,15,32,16)),((30,20,117,4,118),(28,40,47,7,48),(30,43,24,22,25),(30,10,15,67,16)),((30,19,118,6,119),(28,18,47,31,48),(30,34,24,34,25),(30,20,15,61,16)))
    
    # Remainder bits per version
    # From https://www.thonky.com/qr-code-tutorial/structure-final-message
    REMAINDER_LIST = (0, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0, 0)
    
    # Alignment pattern positions per version
    # From https://www.thonky.com/qr-code-tutorial/alignment-pattern-locations
    ALIGNMENT_LIST = ((),(6,18),(6,22),(6,26),(6,30),(6,34),(6,22,38),(6,24,42),(6,26,46),(6,28,50),(6,30,54),(6,32,58),(6,34,62),(6,26,46,66),(6,26,48,70),(6,26,50,74),(6,30,54,78),(6,30,56,82),(6,30,58,86),(6,34,62,90),(6,28,50,72,94),(6,26,50,74,98),(6,30,54,78,102),(6,28,54,80,106),(6,32,58,84,110),(6,30,58,86,114),(6,34,62,90,118),(6,26,50,74,98,122),(6,30,54,78,102,126),(6,26,52,78,104,130),(6,30,56,82,108,134),(6,34,60,86,112,138),(6,30,58,86,114,142),(6,34,62,90,118,146),(6,30,54,78,102,126,150),(6,24,50,76,102,128,154),(6,28,54,80,106,132,158),(6,32,58,84,110,136,162),(6,26,54,82,110,138,166),(6,30,58,86,114,142,170))
    
    # Format information bits
    # From https://www.thonky.com/qr-code-tutorial/format-version-tables
    FORMAT_BITS = (('111011111000100','111001011110011','111110110101010','111100010011101','110011000101111','110001100011000','110110001000001','110100101110110'),('101010000010010','101000100100101','101111001111100','101101101001011','100010111111001','100000011001110','100111110010111','100101010100000'),('011010101011111','011000001101000','011111100110001','011101000000110','010010010110100','010000110000011','010111011011010','010101111101101'),('001011010001001','001001110111110','001110011100111','001100111010000','000011101100010','000001001010101','000110100001100','000100000111011'))
    
    # Version information bits
    # From https://www.thonky.com/qr-code-tutorial/format-version-tables
    VERSION_BITS = (None,None,None,None,None,None,'000111110010010100','001000010110111100','001001101010011001','001010010011010011','001011101111110110','001100011101100010','001101100001000111','001110011000001101','001111100100101000','010000101101111000','010001010001011101','010010101000010111','010011010100110010','010100100110100110','010101011010000011','010110100011001001','010111011111101100','011000111011000100','011001000111100001','011010111110101011','011011000010001110','011100110000011010','011101001100111111','011110110101110101','011111001001010000','100000100111010101','100001011011110000','100010100010111010','100011011110011111','100100101100001011','100101010000101110','100110101001100100','100111010101000001','101000110001101001')
    
    # Patterns used for generating QR code
    FINDER_PATTERN = ModuleMatrix.fromStrList([
        "wwwwwwwww",
        "wbbbbbbbw",
        "wbwwwwwbw",
        "wbwbbbwbw",
        "wbwbbbwbw",
        "wbwbbbwbw",
        "wbwwwwwbw",
        "wbbbbbbbw",
        "wwwwwwwww"
    ])
    
    ALIGNMENT_PATTERN = ModuleMatrix.fromStrList([
        "bbbbb",
        "bwwwb",
        "bwbwb",
        "bwwwb",
        "bbbbb"
    ])
    
    # QR code masks
    MASKS = (
        ModuleMatrix.fromStrList([
            "bw",
            "wb"
        ]),
        ModuleMatrix.fromStrList([
            "b",
            "w"
        ]),
        ModuleMatrix.fromStrList([
            "bww"
        ]),
        ModuleMatrix.fromStrList([
            "bww",
            "wwb",
            "wbw"
        ]),
        ModuleMatrix.fromStrList([
            "bbbwww",
            "bbbwww",
            "wwwbbb",
            "wwwbbb"
        ]),
        ModuleMatrix.fromStrList([
            "bbbbbb",
            "bwwwww",
            "bwwbww",
            "bwbwbw",
            "bwwbww",
            "bwwwww"
        ]),
        ModuleMatrix.fromStrList([
            "bbbbbb",
            "bbbwww",
            "bbwbbw",
            "bwbwbw",
            "bwbbwb",
            "bwwwbb"
        ]),
        ModuleMatrix.fromStrList([
            "bwbwbw",
            "wwwbbb",
            "bwwwbb",
            "wbwbwb",
            "bbbwww",
            "wbbbww"
        ])
    )
    
    def __init__(self, input_data, error_correction_capability = QR_ECC.M):
        """ Generate the smallest possible byte mode QR code with a minimum correction level """
        # Encode string to bytes
        self.data_bytes = input_data.encode()
        
        # Set error correction capability
        self.ecc = error_correction_capability
        
        # Find smallest possible version
        self._findVersion()
        
        # Generate encoded data
        encodedData = self._genEncodedData()
        
        # Generate error corrected data
        dataGroups, ecGroups = self._genErrorCorrection(encodedData)
        
        # Generate interleaved data (final payload)
        payload = self._interleaveGroups(dataGroups, ecGroups)
        
        # Initialize base module matrix
        qrLength = 21 + ((self.version - 1) * 4)
        super().__init__(qrLength, qrLength)
        
        # Generate base matrix with patterns
        self._genBaseMatrix()
        
        # Generate final masks
        finalMasks = self._genFinalMasks()
        
        # Populate base matrix with payload
        self._populateBaseMatrix(payload)
        
        # Generate all masked matrices
        maskedMatrices = self._maskAll(finalMasks)
        
        # Pick best mask
        self._pickBestMask(maskedMatrices)
        
        # Populate format information bits
        self._populateFormatInfoFields()
        
        # Populate version information bits
        self._populateVersionInfoFields()
    
    def _findVersion(self):
        """ Try to find version for smallest code with the minimum given ECC """
        max_ver = len(QRCode.VERSION_LIST)
        max_bytes = QRCode.VERSION_LIST[max_ver - 1][self.ecc]
        
        # Fail if exceeding max capacity
        data_len = len(self.data_bytes)
        if data_len > max_bytes:
            raise QR_Exception("Maximum capacity (version {}) exceeded with given ECC level: {} bytes\nInput data has {} bytes".format(
                max_ver,
                max_bytes,
                data_len
            ))
        
        # Get minimum version
        for i in range(len(QRCode.VERSION_LIST)):
            if QRCode.VERSION_LIST[i][self.ecc] >= data_len:
                self.version = i + 1
                return
    
    def _genEncodedData(self):
        """ Turns input data into a bit stream with headers but no error correction """
        output = BitStream()
        
        # Add mode indicator. Using byte mode, so, write 0100
        output.write([False, True, False, False], bool)
        
        # Add character count indicator. The size of the indicator depends on the QR version in use
        data_len = len(self.data_bytes)
        if self.version <= 9:
            output.write(data_len, uint8)
        else:
            output.write(data_len, uint16)
        
        # Add data
        output.write(self.data_bytes, bytes)
        
        # Get required size
        block_info = QRCode.BLOCK_LIST[self.version - 1][self.ecc]
        req_bytes = None
        if len(block_info) == 3:
            req_bytes = block_info[1] * block_info[2]
        else:
            req_bytes = block_info[1] * block_info[2] + block_info[3] * block_info[4]
        req_bits = req_bytes * 8
        
        # Add 4-bit (or less) zero padding
        zero_count = min(4, req_bits - len(output))
        output.write([False] * zero_count, bool)
        
        # Align data to bytes
        out_len = len(output)
        aligned_bits = ceil(out_len / 8) * 8
        output.write([False] * (aligned_bits - out_len), bool)
        
        # Add padding bytes if necessary
        aligned_bytes = aligned_bits // 8
        alternate = False
        for i in range(req_bytes - aligned_bytes):
            if alternate:
                output.write(17, uint8)
            else:
                output.write(236, uint8)
            alternate = not alternate
        
        return output.read(bytes)
    
    def _genErrorCorrection(self, codewords):
        """ Turn codewords into error-corrected data groups """
        # Get EC info
        block_info = QRCode.BLOCK_LIST[self.version - 1][self.ecc]
        
        # Split into groups of blocks
        groups = ([], [])
        first_block_size = block_info[2]
        for block in range(block_info[1]):
            groups[0].append(codewords[first_block_size * block : first_block_size * (block + 1)])
        
        # Same for second group
        if len(block_info) == 5: # There will be 5 elements in the info tuple if there are 2 groups
            offset = first_block_size * block_info[1]
            second_block_size = block_info[4]
            for block in range(block_info[3]):
                groups[1].append(codewords[offset + second_block_size * block : offset + second_block_size * (block + 1)])
        
        # Do first group's error correction 
        ec_groups = ([], [])
        ecc_codewords = block_info[0]
        rscodec = RSCodec(ecc_codewords)
        for b in range(len(groups[0])):
            # Get full error corrected (EC) codewords as bytes and extract only EC bytes
            ecBytes = rscodec.encode(groups[0][b])[block_info[2]:]
            # Append to list of EC codewords
            ec_groups[0].append(ecBytes)
            
        # Do second group's error correction
        if len(block_info) == 5:
            for b in range(len(groups[1])):
                # Same thing as for first group
                ecBytes = rscodec.encode(groups[1][b])[block_info[4]:]
                ec_groups[1].append(ecBytes)
        
        return groups, ec_groups
    
    def _interleaveGroups(self, dataGroups, ecGroups):
        """ Interleaves data groups into the final bitstream payload, with remainder bits """
        def interleaveTwo(bitStream, first, second):
            # Interleaves two block groups together
            hasSecond = len(second) != 0
            firstLen = len(first[0])
            secondLen = len(second[0]) if hasSecond else 0
            for cw in range(max(firstLen, secondLen)):
                if cw < firstLen:
                    for block in first:
                        bitStream.write(block[cw], uint8)
                if cw < secondLen:
                    for block in second:
                        bitStream.write(block[cw], uint8)
        
        # This is where the payload is stored
        payload = BitStream()
        
        # Interleave data blocks
        interleaveTwo(payload, dataGroups[0], dataGroups[1])
        
        # Interleave EC blocks
        interleaveTwo(payload, ecGroups[0], ecGroups[1])
        
        # Add remainder bits (zero-padding to match size constraints)
        payload.write([False] * QRCode.REMAINDER_LIST[self.version - 1], bool)
        
        return payload
    
    def _genBaseMatrix(self):
        """ Generate the QR code's base matrix, with patterns and reserved areas only """
        length = self.getDimensions()[0]

        # Draw finder patterns (already with separator)
        # This isn't the most efficient way to do things, but then again, neither
        # is making a 2D list and then turning it into an image, so ¯\_(ツ)_/¯
        # Top left
        self.applyPattern(-1, -1, QRCode.FINDER_PATTERN)
        # Top right
        self.applyPattern(length - 8, -1, QRCode.FINDER_PATTERN)
        # Bottom left
        self.applyPattern(-1, length - 8, QRCode.FINDER_PATTERN)

        # Draw alignment patterns
        # Must find all permutations of the coordinate in the alignment table
        # Generate 2-sized permutations for getting 2D coordinate
        patternCoords = QRCode.ALIGNMENT_LIST[self.version - 1]
        endLimit = length - 12
        for x in patternCoords:
            # The coordinates are for the center of the pattern. Find top left
            rx = x - 2
            for y in patternCoords:
                ry = y - 2

                # Don't draw alignment pattern if it overlaps with a finder
                if rx <= 7 and ry <= 7:
                    continue
                if rx <= 7 and ry >= endLimit:
                    continue
                if ry <= 7 and rx >= endLimit:
                    continue
                
                # Draw alignment pattern
                self.applyPattern(rx, ry, QRCode.ALIGNMENT_PATTERN)

        # Add timing pattern
        moduleColor = Module.Black
        for i in range(8, length - 8):
            # Left line
            self[6, i] = moduleColor
            # Top line
            self[i, 6] = moduleColor
            moduleColor = Module.flip(moduleColor)

        # Add reserved black module
        self[8, length - 8] = Module.Black
        
        # Paint reserved format area with bogus modules
        # Bottom left - finder's right
        for y in range(length - 7, length):
            self[8, y] = Module.White

        for i in range(6):
            # Top left - finder's right
            self[8, i] = Module.White
            # Top left - finder's bottom
            self[i, 8] = Module.White

        # Top left - finder's bottom-right corner
        self[7, 8] = Module.White
        self[8, 8] = Module.White
        self[8, 7] = Module.White

        # Top right - finder's bottom
        for x in range(length - 8, length):
            self[x, 8] = Module.White

        # Paint reserved version info area with bogus modules
        # Only applies to versions 7 and above
        if self.version >= 7:
            for i in range(6):
                # Bottom left - finder's top
                self[i, length - 9 ] = Module.White
                self[i, length - 10] = Module.White
                self[i, length - 11] = Module.White
                # Top right - finder's left
                self[length - 9 , i] = Module.White
                self[length - 10, i] = Module.White
                self[length - 11, i] = Module.White
    
    def _genFinalMasks(self):
        """ Generates a list of final masks, those being mask patterns applied to unset parts of the matrix """
        finalMasks = []
        for m in range(8):
            thisFinalMask = self.extractUnset()
            thisFinalMask.applyMaskRepeated(self.MASKS[m])
            finalMasks.append(thisFinalMask)
        return finalMasks
    
    def _populateBaseMatrix(self, payload):
        """ Populates the base matrix with the bitstream payload """
        def drawZigzagCol(x):
            yRange = range(self._height)
            if goingUp:
                yRange = reversed(yRange)
            
            for y in yRange:
                # Skip modules which are already set, since that means they are reserved
                if self[x + 1, y] == Module.Unset:
                    if payload.read(bool):
                        self[x + 1, y] = Module.Black
                    else:
                        self[x + 1, y] = Module.White
                
                if self[x, y] == Module.Unset:
                    if payload.read(bool):
                        self[x, y] = Module.Black
                    else:
                        self[x, y] = Module.White
        
        # Starting at bottom right, populate with payload in a zig-zag pattern
        goingUp = True
        for x in range(self._width - 2, 6, -2):
            drawZigzagCol(x)
            goingUp = not goingUp
        
        # Note that the 7th column is skipped. This is the slice before the 7th column
        for x in range(4, -1, -2):
            drawZigzagCol(x)
            goingUp = not goingUp
    
    def _maskAll(self, finalMasks):
        """ Applies all masks to the matrix with the payload """
        maskedCodes = []
        for mask in finalMasks:
            matrixCopy = self.copy()
            matrixCopy.applyMask(0, 0, mask)
            maskedCodes.append(matrixCopy)
        return maskedCodes
    
    def _pickBestMask(self, maskedMatrices):
        """ Pick the mask that has the least penalty score """
        penaltyScores = []
        for matrix in maskedMatrices:
            score = matrix.getPenaltyScore()
            penaltyScores.append(score)
        
        bestScore = min(penaltyScores)
        for mask in range(8):
            if penaltyScores[mask] == bestScore:
                self.overwrite(maskedMatrices[mask])
                self.mask = mask
                return
    
    def _populateFormatInfoFields(self):
        """ Populate format information fields """
        # Fetch format bits
        formatBitsString = QRCode.FORMAT_BITS[self.ecc][self.mask]
        
        # Turn bits string into module list
        formatBits = []
        for bitStr in formatBitsString:
            if bitStr == '1':
                formatBits.append(Module.Black)
            else:
                formatBits.append(Module.White)
        
        # Bottom left - finder's right
        for dy in range(7):
            self[8, self._height - 1 - dy] = formatBits[dy]
        
        # Top left - finder's bottom
        for dx in range(6):
            self[dx, 8] = formatBits[dx]
        
        # Top left - finder's bottom right corner
        self[7, 8] = formatBits[6]
        self[8, 8] = formatBits[7]
        self[8, 7] = formatBits[8]
        
        # Top left - finder's right
        for dy in range(6):
            self[8, 5 - dy] = formatBits[9 + dy]
        
        # Top right - finder's bottom
        for dx in range(8):
            self[self._width - 8 + dx, 8] = formatBits[7 + dx]
    
    def _populateVersionInfoFields(self):
        """ Populate version information fields """
        # Don't do anything if below version 7
        if self.version < 7:
            return
        
        # Fetch version bits
        versionBitsString = QRCode.VERSION_BITS[self.version - 1]
        
        # Turn bits string into module list
        versionBits = []
        for bitStr in versionBitsString:
            if bitStr == '1':
                versionBits.append(Module.Black)
            else:
                versionBits.append(Module.White)
        
        # Bottom left - finder's top
        dx = dy = 0
        for i in range(18):
            # Goes from bottom right to top left
            # 17 14 11 8  5  2
            # 16 13 10 7  4  1
            # 15 12 9  6  3  0
            
            # Set module
            self[5 - dx, self._height - 9 - dy] = versionBits[i]
            
            # Move up
            dy += 1
            # Wrap around if necessary
            if dy == 3:
                dy = 0
                dx += 1
        
        # Top right - finder's left
        dx = dy = 0
        for i in range(18):
            # Goes from bottom left to top right
            # 17 16 15
            # 14 13 12
            # 11 10 9
            # 8  7  6
            # 5  4  3
            # 2  1  0
            
            # Set module
            self[self._width - 9 - dx, 5 - dy] = versionBits[i]
            
            # Move left
            dx += 1
            # Wrap around if necessary
            if dx == 3:
                dx = 0
                dy += 1

if __name__ == '__main__':
    qr = QRCode("https://www.google.com/search?q=qr+code")
    print("Encoded as version {}, ECC {}, mask {}. Saved as output.png".format(qr.version, QR_ECC.asString(qr.ecc), qr.mask))
    qr.toImage().show()
    qr.toImage().save("output.png", "PNG")
