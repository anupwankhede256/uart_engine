import nidigital

def create_session(resource_name, pinmap_path):
    session = nidigital.Session(
        resource_name=resource_name,
        options={"simulate": True,
                 "driver_setup":{
                     "Model":"6571"
                 }}
    )

    session.load_pin_map(pinmap_path)
    return session

def configure_uart_levels(session):

    # -------- TX PIN --------
    session.channels["TX_PIN"].configure_voltage_levels(
        vil=0.8,
        vih=2.0,
        vol=0.8,
        voh=2.6,
        vterm=0.0
    )

    session.channels["TX_PIN"].configure_active_load_levels(
        iol=0.002,      # 2 mA
        ioh=-0.002,     # -2 mA
        vcom=3.3
    )

    session.channels["TX_PIN"].termination_mode = (
        nidigital.TerminationMode.ACTIVE_LOAD
    )

    # -------- RX PIN --------
    session.channels["RX_PIN"].configure_voltage_levels(
        vil=0.8,
        vih=2.0,
        vol=0.8,
        voh=2.6,
        vterm=0.0
    )

    session.channels["RX_PIN"].termination_mode = (
        nidigital.TerminationMode.HIGH_Z
    )

    print("\n========== PIN LEVEL CONFIG ==========")
    print("VIH               : 2.0 V")
    print("VIL               : 0.8 V")
    print("VOH               : 2.6 V")
    print("VOL               : 0.8 V")
    print("TX Termination    : ACTIVE_LOAD")
    print("RX Termination    : HIGH_Z")
    print("VCOM              : 3.3 V")
    print("IOL               : 2 mA")
    print("IOH               : -2 mA")
    print("======================================\n")

def load_and_run_pattern(session, digipat_path, pattern_name,
                         waveform_bits, loop_count, test_mode):

    session.load_pattern(digipat_path)

    # ==================================================
    # TX MODE
    # ==================================================
    if test_mode == "tx":

        waveform_name = "new_waveform"

        session.pins["TX_PIN"].create_source_waveform_serial(
            waveform_name=waveform_name,
            data_mapping=nidigital.SourceDataMapping.BROADCAST,
            sample_width=8,
            bit_order=nidigital.BitOrder.MSB
        )

        session.write_source_waveform_broadcast(
            waveform_name,
            waveform_bits
        )

        session.write_sequencer_register(
            nidigital.SequencerRegister.REGISTER0,
            loop_count
        )

        results = session.burst_pattern(pattern_name)
        print("Burst Results:", results)

    # ==================================================
    # LOOPBACK MODE
    # ==================================================
    elif test_mode == "lb":

        waveform_name = "new_waveform"

        # ---- TX SOURCE ----
        session.pins["TX_PIN"].create_source_waveform_serial(
            waveform_name=waveform_name,
            data_mapping=nidigital.SourceDataMapping.BROADCAST,
            sample_width=8,
            bit_order=nidigital.BitOrder.MSB
        )

        session.write_source_waveform_broadcast(
            waveform_name,
            waveform_bits
        )

        # ---- RX CAPTURE ----
        session.pins["RX_PIN"].create_capture_waveform_serial(
            waveform_name=waveform_name,
            sample_width=8,
            bit_order=nidigital.BitOrder.LSB
        )

        session.write_sequencer_register(
            nidigital.SequencerRegister.REGISTER0,
            loop_count
        )

        session.burst_pattern(pattern_name)

        data = session.fetch_capture_waveform(
            waveform_name,
            samples_to_read=loop_count
        )

        print("Loopback Capture:", data)

    # ==================================================
    # RX MODE
    # ==================================================
    elif test_mode == "rx":

        capture_waveform = "read"

        session.pins["RX_PIN"].create_capture_waveform_serial(
            waveform_name=capture_waveform,
            sample_width=8,
            bit_order=nidigital.BitOrder.LSB
        )

        session.write_sequencer_register(
            nidigital.SequencerRegister.REGISTER0,
            loop_count
        )

        session.burst_pattern(pattern_name)

        data = session.fetch_capture_waveform(
            waveform_name=capture_waveform,
            samples_to_read=loop_count
        )

        print("Captured Data:", data)