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
        if test_mode == "loopback":
            f.write("timeset Idle_test;\n")
            f.write("timeset UART_LB;\n\n")
        else:
            f.write("timeset time_uart;\n\n")
            
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
        elif test_mode == "rx":

            EDGE_REPEAT = 80
            BIT_REPEAT = 819

            f.write(f"    set_loop(reg0) time_uart X;\n")
            f.write("    capture_start(read) time_uart X;\n\n")

            f.write(f"Start: repeat({EDGE_REPEAT}), match time_uart L;\n")
            f.write("FindFallingEdge: jump_if(matched, FindFallingEdge) time_uart X;\n")
            f.write("FindRisingEdge: jump_if(!matched, FindRisingEdge) time_uart X;\n\n")

            # First data bit attached to label
            f.write(f"read: repeat({BIT_REPEAT}) time_uart X;\n")
            f.write("    capture time_uart V;\n")

            # Remaining 7 bits
            for _ in range(7):
                f.write(f"    repeat({BIT_REPEAT}) time_uart X;\n")
                f.write("    capture time_uart V;\n")

            # Stop bit
            f.write(f"    repeat({BIT_REPEAT}) time_uart X;\n")
            f.write("    time_uart H;\n\n")

            f.write("    end_loop(Start) time_uart X;\n")
            f.write("    capture_stop time_uart X;\n")
            f.write("    halt time_uart X;\n")
            f.write("}\n")

        # -------------------------------------------------
        # LOOPBACK MODE
        # -------------------------------------------------
        elif test_mode == "loopback":

            BIT_REPEAT = 819
            EDGE_REPEAT = 80

            f.write("  set_loop(reg0) Idle_test X X;\n")
            f.write("  source_start(new_waveform) UART_LB X X;\n\n")

            #-----------------------TX SECTION------------------------------
            f.write("START_y: UART_LB 0 X;\n")

            f.write("  repeat(8), source UART_LB D X;\n")
            f.write("  UART_LB 1 X;\n")
            f.write("  end_loop(START_y) X X;\n\n")

            #-----------------------RX SECTION------------------------------
            f.write("  set_loop(reg0) Idle_test X X;\n")
            f.write("  capture_start(new_waveform) Idle_test X X;\n\n")

            f.write(f"st: repeat({EDGE_REPEAT}), match Idle_test X L;\n")
            f.write("FindFallingEdge: jump_if(matched, FindFallingEdge) Idle_test X L:\n")
            f.write("FindRisingEdge: jump_if(!matched, FindRisingEdge) Idle_test X L;\n\n")

            f.write("read:\n")

            for _ in range(8):
                f.write(f"  repeat({BIT_REPEAT}) Idle_test X X;\n")
                f.write("  capture Idle_test X V;\n")

            f.write(f"  repeat({BIT_REPEAT}) Idle_test X X;\n")
            f.write("  Idle_test X H;\n\n")

            f.write("  end_loop(st) X X;\n")
            f.write("  capture_stop Idle_test X X;\n")
            f.write("  halt Idle_test X X;\n")
            f.write("}\n")