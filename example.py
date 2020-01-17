from helpers import Waveform
from controller import Controller
from controller.drivers.connection import ZIDeviceConnection
import numpy as np
import time


if __name__ == "__main__":

    c = Controller()
    c.setup("resources/connection.json")
    c.connect_device("hdawg0")

    awg0 = 0
    awg1 = 1

    c.set(
        [
            (f"/awgs/{awg1}/auxtriggers/*/slope", 1),  # trigger to Rise
            (f"/awgs/{awg1}/auxtriggers/*/channel", 2),  # Trigger In 3
            ("/awgs/*/single", 0),  # Rerun
            ("/sigouts/0/on", 1),
            ("/sigouts/2/on", 1),
        ]
    )

    amps = np.linspace(0, 1, 101)
    reps = 10000
    period = 100e-6

    settings = dict(
        sequence_type="Rabi",
        trigger_mode="Send Trigger",
        pulse_amplitudes=amps,
        pulse_width=30e-9,
        pulse_truncation=4,
        period=period,
        repetitions=reps,
    )
    c.awg_set_sequence_params(awg0, **settings)
    c.compile_program(awg0)

    settings = dict(
        sequence_type="Simple",
        trigger_mode="External Trigger",
        latency=100e-9,
        period=period,
        repetitions=reps * len(amps),
    )
    c.awg_set_sequence_params(awg1, **settings)
    c.awg_queue_waveform(awg1, Waveform(np.ones(2000), []))
    c.awg_upload_waveforms(awg1)

    # run AWGs, slave first
    c.awg_run(awg1)
    c.awg_run(awg0)

    print("Done!")