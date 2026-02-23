# input_validator.py

VALID_PARITY = {"None", "Even", "Odd"} #set

# defines validation function
def validate_inputs(test_name, baud, data_bits, parity, stop_bits, tx_data,test_type):
    if not test_name or not test_name.strip():
        raise ValueError("Test name cannot be empty")

    if not (300 <= baud <= 115200):
        raise ValueError("Baud rate must be between 300 and 115200")

    if data_bits != 8:
        raise ValueError("Only 8 data bits supported")

    if parity not in VALID_PARITY:
        raise ValueError("Parity must be None, Even, or Odd")

    if stop_bits not in (1, 2):
        raise ValueError("Stop bits must be 1 or 2")

    if test_type == "tx" and not tx_data:
        raise ValueError("Transmission data cannot be empty")

    return True
