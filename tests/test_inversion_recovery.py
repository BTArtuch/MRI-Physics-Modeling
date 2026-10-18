import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings, strategies as st

# We will build this function in the next step to satisfy these tests.
# It should return a DataFrame with columns: ['Time', 'Mz', 'Mxy', 'Mx_rot', 'My_rot']
from src.ir.simulate import generate_ir_trajectory

# ---------------------------------------------------------
# Pytest: Fixed Edge Cases & Fundamental Physics
# ---------------------------------------------------------

def test_initial_180_inversion():
    """
    The 180-degree pulse cleanly flips Mz from 1.0 to -1.0.
    """
    df = generate_ir_trajectory(t1=1.0, t2=0.1, ti=0.5, dt=0.001, t_180=0.5, t_90=0.25)
    
    # At the exact end of the 180 pulse, Mz should be fully inverted
    end_of_180_idx = int(0.5 / 0.001)
    mz_at_inversion = df['Mz'].iloc[end_of_180_idx]
    
    assert mz_at_inversion == pytest.approx(-1.0, abs=1e-3), \
        f"180 pulse failed: Expected Mz to be -1.0, got {mz_at_inversion}"

def test_inversion_recovery_null_point():
    """
    If TI = T1 * ln(2) = 0.693 * T1, Mz must be zero right before the 90-degree pulse.
    """
    t1_val = 1.0
    ti_null = t1_val * np.log(2)  # ~0.693 seconds
    t_180 = 0.1
    
    df = generate_ir_trajectory(t1=t1_val, t2=0.1, ti=ti_null, dt=0.001, t_180=t_180, t_90=0.1)
    
    # Calculate the index right before the 90-degree pulse begins
    end_of_ti_idx = int((t_180 + ti_null) / 0.001)
    mz_at_null = df['Mz'].iloc[end_of_ti_idx]
    
    assert mz_at_null == pytest.approx(0.0, abs=1e-2), \
        f"Null point failed: Expected Mz to be 0.0 at TI=0.693*T1, got {mz_at_null}"

def test_90_degree_readout():
    """
    The 90-degree read pulse accurately tips the available Mz 
    into the transverse plane (Mxy) to produce the FID.
    """
    # Using a short TI so Mz is still negative when the 90 pulse hits
    df = generate_ir_trajectory(t1=1.0, t2=0.1, ti=0.2, dt=0.001, t_180=0.1, t_90=0.1)
    
    start_90_idx = int((0.1 + 0.2) / 0.001)
    end_90_idx = int((0.1 + 0.2 + 0.1) / 0.001)
    
    mz_before_90 = df['Mz'].iloc[start_90_idx]
    mxy_after_90 = df['Mxy'].iloc[end_90_idx]
    
    # The transverse magnitude after the 90 pulse must equal the absolute 
    # longitudinal magnitude available right before the pulse.
    assert mxy_after_90 == pytest.approx(abs(mz_before_90), abs=1e-2), \
        "90 pulse failed to conserve magnetization magnitude during tip-down"

# ---------------------------------------------------------
# Hypothesis: Property-Based Testing
# ---------------------------------------------------------

@given(
    t1=st.floats(min_value=0.5, max_value=3.0),
    ti=st.floats(min_value=0.1, max_value=2.0)
)
@settings(max_examples=50)
def test_longitudinal_recovery_equation(t1, ti):
    """
    No matter what T1 or TI is randomly generated, the trajectory 
    during the free relaxation phase MUST strictly follow Mz(t) = 1 - 2*exp(-t/T1).
    """
    t_180 = 0.1
    dt = 0.002
    
    df = generate_ir_trajectory(t1=t1, t2=0.1, ti=ti, dt=dt, t_180=t_180, t_90=0.1)
    
    # Sample a time point exactly halfway through the TI relaxation period
    test_time_relative = ti / 2.0
    absolute_time = t_180 + test_time_relative
    test_idx = int(absolute_time / dt)
    
    simulated_mz = df['Mz'].iloc[test_idx]
    
    # Calculate the true mathematical expectation based on the IR equation
    expected_mz = 1.0 - 2.0 * np.exp(-test_time_relative / t1)
    
    assert simulated_mz == pytest.approx(expected_mz, abs=1e-2), \
        f"IR recovery equation failed for T1={t1}, TI={ti}. Expected {expected_mz}, got {simulated_mz}"

@given(
    t1=st.floats(min_value=0.5, max_value=2.0),
    t2=st.floats(min_value=0.05, max_value=0.3)
)
@settings(max_examples=50)
def test_magnetization_conservation(t1, t2):
    """
    The total magnetization magnitude (sqrt(Mz^2 + Mxy^2)) 
    must never exceed 1.0 + margin of error at any point during the sequence.
    """
    df = generate_ir_trajectory(t1=t1, t2=t2, ti=0.5, dt=0.002, t_180=0.1, t_90=0.1)
    
    total_magnitude = np.sqrt(df['Mz']**2 + df['Mxy']**2)
    max_magnitude = total_magnitude.max()
    
    assert max_magnitude <= 1.01, \
        f"Physics violation: Net magnetization vector exceeded M0 (Magnitude: {max_magnitude})"