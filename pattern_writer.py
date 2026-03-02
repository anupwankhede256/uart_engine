def write_digipatsrc(
    file_path,
    pattern_name,
    pin_name,
    parity,
    stop_bits,
    baud_rate,
    test_mode="tx",
    rx_count = None
):

    REPEAT_TABLE = {
        9600: 3,
        14400: 3,
        19200: 3,
        4800: 6,
        2400: 11,
        1200: 22,
        600: 42,
        300: 84
    }

    if baud_rate in [28800, 38400, 57600, 115200]:
        repeat_factor = 1
    else:
        repeat_factor = REPEAT_TABLE.get(baud_rate, 1)

    with open(file_path, "w") as f:

        f.write("file_format_version 1.1;\n\n")
        if test_mode == "lb":
            f.write("timeset Idle_test;\n")
            f.write("timeset UART_LB;\n\n")
        else:
            f.write("timeset time_uart;\n\n")

        if test_mode == "lb":
            f.write(f"pattern {pattern_name} (TX_PIN,RX_PIN)\n")
        else:
            f.write(f"pattern {pattern_name} ({pin_name})\n")
        f.write("{\n")

        # -------------------------------------------------
        # TRANSMISSION MODE
        # -------------------------------------------------
        if test_mode == "tx":

            f.write("    time_uart X;\n\n")
            f.write("    source_start(new_waveform) time_uart X;\n")
            f.write("    set_loop(reg0) time_uart X;\n\n")

            # Start bit
            if repeat_factor > 1:
                f.write(f"start: repeat({repeat_factor}) time_uart 0;\n\n")
            else:
                f.write("start: time_uart 0;\n\n")

            # Data bits
            for _ in range(8):
                if repeat_factor > 1:
                    f.write(f"    repeat({repeat_factor}), source time_uart D;\n")
                else:
                    f.write("    source time_uart D;\n")

            # Parity
            if parity != "None":
                if repeat_factor > 1:
                    f.write(f"    repeat({repeat_factor}), source time_uart D;\n")
                else:
                    f.write("    source time_uart D;\n")

            # Stop bits
            for _ in range(stop_bits):
                if repeat_factor > 1:
                    f.write(f"    repeat({repeat_factor}) time_uart 1;\n")
                else:
                    f.write("    time_uart 1;\n")

            f.write("\n")
            f.write("    end_loop(start) time_uart X;\n")
            f.write("    halt time_uart X;\n")
            f.write("}\n")

        # -------------------------------------------------
        # RECEPTION MODE
        # -------------------------------------------------
        elif test_mode == "lb":

            BIT_REPEAT = 819
            EDGE_REPEAT = 80

            # TX section
            f.write("    set_loop(reg0) Idle_test XX;\n\n")

            f.write("    source_start(new_waveform) UART_LB XX;\n")
            f.write("    UART_LB 1X;\n\n")

            f.write("START_y:\n")
            f.write("    UART_LB 0X;\n")
            f.write("    repeat(8), source UART_LB DX;\n")
            f.write("    UART_LB 1X;\n")
            f.write("    end_loop(START_y) Idle_test XX;\n\n")

            # RX section
            f.write("    set_loop(reg0) Idle_test XX;\n")
            f.write("    capture_start(new_waveform) Idle_test XX;\n\n")

            f.write("st:\n")
            f.write(f"    repeat({EDGE_REPEAT}), match Idle_test XL;\n\n")

            f.write("FindFallingEdge:\n")
            f.write("    jump_if(matched, FindFallingEdge) Idle_test XX;\n\n")

            f.write("FindRisingEdge:\n")
            f.write("    jump_if(!matched, FindRisingEdge) Idle_test XX;\n\n")

            f.write("read:\n")

            for _ in range(8):
                f.write(f"    repeat({BIT_REPEAT}) Idle_test XX;\n")
                f.write("    capture Idle_test XV;\n")

            f.write(f"    repeat({BIT_REPEAT}) Idle_test XX;\n")
            f.write("    Idle_test XH;\n\n")

            f.write("    end_loop(st) Idle_test XX;\n")
            f.write("    capture_stop Idle_test XX;\n")
            f.write("    halt Idle_test XX;\n")

            f.write("}\n")