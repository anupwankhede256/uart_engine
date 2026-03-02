from input_validator import validate_inputs 
from wavefrom_builder import build_waveform_bits, calculate_loop_count
from pattern_writer import write_digipatsrc
from compile_interface import compile_pattern
from timing_configurator import configure_uart_timing
from ni_session_manager import create_session, load_and_run_pattern, configure_uart_levels

def main():
    test_name = input("Test Name: ")
    test_type = input("Test Mode (tx/rx/lb): ").strip().lower()
    baud = int(input("Baud Rate: "))
    parity = input("Parity (None/Even/Odd): ")
    stop_bits = int(input("Stop Bits (1/2): "))

    tx_data = None
    rx_count = None
    if test_type == "tx":
        tx_data = input("Transmission Data: ")
    elif test_type == "rx":
        rx_count = int(input("Number to characters to receive: "))
    elif test_type == "lb":
        tx_data = input("Transmission Data: ")
        rx_count = len(tx_data)
    else:
        raise ValueError("invalid Test Type")

    validate_inputs(test_name, baud, 8, parity, stop_bits, tx_data,test_type)

    if test_type in ("tx","lb"):
        waveform_bits = build_waveform_bits(tx_data, parity)
        loop_count = calculate_loop_count(tx_data)
    elif test_type == "rx":
        waveform_bits = None
        loop_count = rx_count
    else:
        waveform_bits = None
        loop_count = None

    src_file = f"{test_name}.digipatsrc"
    out_file = f"{test_name}.digipat"
    pinmap = r"C:\Users\anupsw\Documents\NI-DIGITAL API CODE\uart_engine\Pinmaps\PinMap.pinmap"

    if test_type == "tx":
        pin = "TX_PIN"
        mode = "tx"
    elif test_type == "rx":
        pin = "RX_PIN" 
        mode = "rx"
    elif test_type == "lb":
        pin = "UART_PINS"
        mode = "lb"
    else:
        raise ValueError("Invalid test type")
    write_digipatsrc(
        src_file,
        test_name,
        pin,
        parity,
        stop_bits,
        baud,
        test_mode = mode,
        rx_count = rx_count
    )

    compile_pattern(src_file, out_file, pinmap)

    session = create_session("PXI1Slot3", pinmap)

    configure_uart_levels(session)

    configure_uart_timing(session, baud, test_type)

    if test_type in ("tx","lb"):
        load_and_run_pattern(
            session,
            out_file,
            test_name,
            waveform_bits,
            loop_count,
            test_type
        )
    else:
        load_and_run_pattern(
            session,
            out_file,
            test_name,
            None,
            rx_count,
            test_type
        )

if __name__ == "__main__":
    main()
