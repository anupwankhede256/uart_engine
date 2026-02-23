# timing_configurator.py

import nidigital

def configure_uart_timing(session, baud_rate, test_mode):

    try:
        session.create_time_set("time_uart")
    except nidigital.Error:
        pass

    # -----------------------------
    # RECEPTION MODE (Fixed Timing)
    # -----------------------------
    if test_mode == "rx":

        # Constant tester period for all baud rates
        period = 4.0650406504065e-6  # seconds

        session.configure_time_set_period("time_uart", period)

        session.pins["UART_PINS"].configure_time_set_edge_multiplier("time_uart", 1)

        session.pins["UART_PINS"].configure_time_set_drive_format(
            "time_uart",
            nidigital.DriveFormat.NR
        )

        # Drive edges (NR format, no active drive)
        session.pins["UART_PINS"].configure_time_set_drive_edges(
            "time_uart",
            nidigital.DriveFormat.NR,
            drive_on_edge=0.0,
            drive_data_edge=0.0,
            drive_return_edge=0.0,
            drive_off_edge=period
        )

        # Compare strobe at half period
        session.pins["UART_PINS"].configure_time_set_compare_edges_strobe(
            "time_uart",
            strobe_edge=period / 2
        )

        print("\n========== RX TIMESET CONFIG ==========")
        print(f"Mode                 : RX")
        print(f"Period (µs)          : {period * 1e6:.6f}")
        print(f"Compare Strobe (µs)  : {(period/2) * 1e6:.6f}")
        print("Edge Multiplier      : 1x")
        print("Drive Format         : NR")
        print("=======================================\n")

        return period
    
    # -----------------------------
    # LOOPBACK MODE (Dynamic)
    # -----------------------------
    elif test_mode == "loopback":

        bit_period = 1/baud_rate

        session.create_time_set("UART_LB")
        session.pins["TX_PIN"].configure_time_set_period("UART_LB", bit_period)
        session.pins["TX_PIN"].configure_timme_set_drive_format(
            "UART_LB",
            nidigital.DriveFormat.NR
        )
        session.pins["TX_PIN"].configure_time_set_drive_edges(
            "UART_LB",
            nidigital.DriveFormat.NR,
            0.0,
            0.0,
            0.0,
            bit_period
        )
        
        session.pins["TX_PIN"].configure_time_set_compare_edges_strobe(
            "UART_LB",
            bit_period/2
        )

        # RX timset
        rx_period = bit_period / 820

        session.create_time_set("Idle_test")

        session.pins["UART_PINS"].configure_time_set_period("Idle_test", rx_period)
        session.pins["UART_PINS"].configure_time_set_drive_format(
            "Idle_test",
            nidigital.DriveFormat.NR
        )
        session.pins["UART_PINS"].configure_time_set_drive_edges(
            "Idle_test",
            nidigital.DriveFormat.NR,
            0.0,
            0.0,
            0.0,
            rx_period
        )
        session.pins["UART_PINS"].configure_time_set_compare_edges_strobe(
            "Idle_test",
            rx_period
        )

        print("\n========== LOOPBACK TIMESET CONFIG ==========")
        print(f"TX Period (µs)  : {bit_period * 1e6:.6f}")
        print(f"RX Period (ns)  : {rx_period * 1e9:.6f}")
        print("=============================================\n")

    # -----------------------------
    # TRANSMISSION MODE (Dynamic)
    # -----------------------------
    else:

        bit_period = 1.0 / baud_rate

        # Determine divider
        divider_table = {
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
            divider = 1
        else:
            divider = divider_table.get(baud_rate, 1)

        period = bit_period / divider

        session.configure_time_set_period("time_uart", period)

        session.pins["UART_PINS"].configure_time_set_edge_multiplier("time_uart", 1)

        session.pins["UART_PINS"].configure_time_set_drive_format(
            "time_uart",
            nidigital.DriveFormat.NR
        )

        # Drive edges (TX drives data)
        session.pins["UART_PINS"].configure_time_set_drive_edges(
            "time_uart",
            nidigital.DriveFormat.NR,
            drive_on_edge=0.0,
            drive_data_edge=100e-9,  # 100 ns
            drive_return_edge=0.0,
            drive_off_edge=period
        )

        session.pins["UART_PINS"].configure_time_set_compare_edges_strobe(
            "time_uart",
            strobe_edge=period / 2
        )

        print("\n========== TX TIMESET CONFIG ==========")
        print(f"Mode                 : TX")
        print(f"Baud Rate            : {baud_rate}")
        print(f"Bit Period (µs)      : {(1/baud_rate)*1e6:.6f}")
        print(f"Vector Period (µs)   : {period * 1e6:.6f}")
        print(f"Divider Used         : {divider}")
        print(f"Compare Strobe (µs)  : {(period/2) * 1e6:.6f}")
        print("Edge Multiplier      : 1x")
        print("Drive Format         : NR")
        print("Drive Data Edge      : 100 ns")
        print("=======================================\n")

        return period
