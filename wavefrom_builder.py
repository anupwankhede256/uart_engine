# wavefrom_builder.py
#this function encapsulates logic for covering transmit data into a waveform bit list.
# tx_data = string, data to transmit.
# parity = parity configuration
def build_waveform_bits(tx_data, parity):
    """
    Returns waveform bit list for source memory.
    Only includes data bits (+ parity if enabled).
    Start/Stop bits are handled in pattern.
    """
    # Creates an empty list named waveform_bits. This list will accumulate all bits generated from all characters.{empty list}
    waveform_bits = []

    for char in tx_data: # iterates over each element in tx_data.
        val = ord(char) # ord() returns ASCII integer value.

        # creates a list of 8 bits extracted from integer val.
        #range(8) generates integers:0,1,2,3,4,5,6,7
        # val >> i : right shift operaiton, shifts bits right by i. for example: val = 65 (01000001)
        # & 1 masks all bits except LSB (least significant bit), this extracts bit at position i.
        # result = [10000010]
        data_bits = [(val >> i) & 1 for i in range(8)] 
        waveform_bits.extend(data_bits) # appends all 8 bits into waveform_bits. Builds continuous wavefrom stream.

        # Parity calculation
        if parity != "None":
            ones = sum(data_bits) # Counts number of 1 bits.

            if parity == "Even":
                parity_bit = ones % 2
            else:  # Odd
                parity_bit = (ones + 1) % 2

            waveform_bits.append(parity_bit)

    return waveform_bits

# defines function to calculate number of loops.
def calculate_loop_count(tx_data):
    """
    One loop per character.
    """
    return len(tx_data) # returns number of characters in tx_data.
