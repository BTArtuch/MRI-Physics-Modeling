import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings, strategies as st

# We will build this function in the next step to satisfy these tests.
from src.spin_echo.simulate import generate_se_trajectory

# ---------------------------------------------------------
# Pytest: Fixed Edge Cases & Fundamental Physics
# ---------------------------------------------------------

def test_initial_90_excitation():
    """
    Validates Phase 1: The 90-degree pulse cleanly tips Mz into the transverse plane.
    """
    df = generate_se_trajectory(t1=1.0, t2=0.1, te=0.5, dt=0.001, t_90=0.05, t_180=0.05)
    
    # At the exact end of the 90 pulse, Mxy should be near maximum (1.0) and Mz near 0
    end_of_90_idx = int(0.05 / 0.001)
    mz_at_excitation = df['Mz'].iloc[end_of_90_idx]
    mxy_at_excitation = df['Mxy_net'].iloc[end_of_90_idx]
    mx_at_excitation = df['Mx'].iloc[end_of_90_idx]
    my_at_excitation = df['My'].iloc[end_of_90_idx]
    
    assert mz_at_excitation == pytest.approx(0.0, abs=1e-2), \
        f"90 pulse failed: Expected Mz to be 0.0, got {mz_at_excitation}"
    assert mxy_at_excitation == pytest.approx(1.0, abs=1e-2), \
        f"90 pulse failed: Expected Mxy to be 1.0, got {mxy_at_excitation}"
    assert mx_at_excitation == pytest.approx(0.0, abs=1e-2)
    assert my_at_excitation == pytest.approx(1.0, abs=1e-2)

def test_transverse_signal_decays_gradually_after_excitation():
    """
    Transverse signal should start near 1 after the 90 pulse and dephase over
    time, rather than disappearing immediately.
    """
    dt = 0.001
    df = generate_se_trajectory(t1=1.0, t2=0.6, te=0.8, dt=dt, t_90=0.1, t_180=0.1)

    end_of_90_idx = int(0.1 / dt)
    shortly_after_90 = df["Mxy_net"].iloc[end_of_90_idx + 1]
    halfway_to_180 = df["Mxy_net"].iloc[int(0.3 / dt)]
    near_180 = df["Mxy_net"].iloc[int(0.5 / dt)]

    assert shortly_after_90 > 0.95
    assert shortly_after_90 > halfway_to_180 > near_180 > 0.0

def test_spin_echo_rephasing():
    """
    Validates the exact textbook Spin Echo rephasing.
    At TE = 2 * tau, the net transverse magnetization (Mxy_net) must peak.
    """
    te_val = 0.4
    t_90 = 0.05
    t_180 = 0.05
    
    df = generate_se_trajectory(t1=1.0, t2=0.1, te=te_val, dt=0.001, t_90=t_90, t_180=t_180)
    
    # Calculate the index for the Echo Time (TE)
    echo_idx = int((t_90 + te_val/2 + t_180 + te_val/2) / 0.001)
    
    # The signal at TE should be higher than the signal just before and just after the echo
    mxy_at_echo = df['Mxy_net'].iloc[echo_idx]
    mxy_before_echo = df['Mxy_net'].iloc[echo_idx - 50]
    mxy_after_echo = df['Mxy_net'].iloc[echo_idx + 50]
    
    assert mxy_at_echo > mxy_before_echo, "Signal failed to rephase at TE."
    assert mxy_at_echo > mxy_after_echo, "Signal failed to decay after TE."

def test_longitudinal_magnetization_recovers_from_180_pulse_inversion():
    """
    The 180-degree pulse should leave Mz negative, followed by gradual T1
    recovery toward equilibrium rather than an immediate return to positive Mz.
    """
    dt = 0.001
    t_90 = 0.05
    te = 0.4
    t_180 = 0.05
    pulse_start = t_90 + te / 2
    pulse_end = pulse_start + t_180
    df = generate_se_trajectory(
        t1=1.0, t2=0.1, te=te, dt=dt, t_90=t_90, t_180=t_180
    )

    mz_at_pulse_end = df["Mz"].iloc[int(pulse_end / dt)]
    mz_shortly_after = df["Mz"].iloc[int((pulse_end + 0.01) / dt)]
    mz_later = df["Mz"].iloc[int((pulse_end + 0.2) / dt)]

    assert mz_at_pulse_end < 0.0
    assert mz_shortly_after < 0.0
    assert mz_at_pulse_end < mz_shortly_after < mz_later < 1.0

def test_positive_mx_rf_pulse_rotates_between_mz_and_my():
    """
    With B1 along +Mx, a 180-degree pulse rotates +Mz through +My and into -Mz.
    """
    dt = 0.001
    t_90 = 0.05
    te = 0.4
    t_180 = 0.05
    pulse_start = t_90 + te / 2
    pulse_midpoint = pulse_start + t_180 / 2
    pulse_end = pulse_start + t_180
    df = generate_se_trajectory(
        t1=1.0, t2=0.1, te=te, dt=dt, t_90=t_90, t_180=t_180
    )

    mz_before_pulse = df["Mz"].iloc[int(pulse_start / dt)]
    my_midpulse = df["My"].iloc[int(pulse_midpoint / dt)]
    mz_midpulse = df["Mz"].iloc[int(pulse_midpoint / dt)]
    my_after_pulse = df["My"].iloc[int(pulse_end / dt)]

    assert my_midpulse == pytest.approx(mz_before_pulse, abs=1e-2)
    assert mz_midpulse == pytest.approx(0.0, abs=1e-2)
    assert my_after_pulse < 0.0

# ---------------------------------------------------------
# Hypothesis: Property-Based Testing
# ---------------------------------------------------------

@given(
    te=st.floats(min_value=0.2, max_value=1.0)
)
@settings(max_examples=50)
def test_echo_time_accuracy(te):
    """
    Property Test: No matter what TE is randomly generated, the maximum 
    transverse signal after the 180 pulse MUST occur exactly at TE.
    """
    t_90 = 0.05
    t_180 = 0.05
    dt = 0.002
    
    df = generate_se_trajectory(t1=1.0, t2=0.2, te=te, dt=dt, t_90=t_90, t_180=t_180)
    
    # Isolate the data after the 180 pulse
    start_of_rephasing = int((t_90 + te/2 + t_180) / dt)
    df_rephasing = df.iloc[start_of_rephasing:]
    
    # Find the time of the maximum signal in this window
    max_signal_idx = df_rephasing['Mxy_net'].idxmax()
    simulated_te_time = df.loc[max_signal_idx, 'Time']
    
    expected_te_time = t_90 + te/2 + t_180 + te/2
    
    assert simulated_te_time == pytest.approx(expected_te_time, abs=dt*2), \
        f"Echo occurred at {simulated_te_time}, expected {expected_te_time}"