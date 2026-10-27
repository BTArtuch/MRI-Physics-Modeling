import numpy as np
import pandas as pd


def generate_se_trajectory(t1, t2, te, dt, t_90, t_180):
	"""Simulate a spin echo and return its magnetization as a DataFrame.

	The RF field is along positive Mx, so the positive 90-degree excitation
	rotates equilibrium Mz toward positive My.
	``te`` is the interval from the center of the 90° pulse to the center of
	the 180° pulse. With finite pulse durations, the echo occurs at
	``t_90 + te + t_180``.
	"""
	if any(value <= 0 for value in (t1, t2, te, dt, t_90, t_180)):
		raise ValueError("t1, t2, te, dt, t_90, and t_180 must be positive")

	pulse_180_start = t_90 + te / 2
	pulse_180_end = pulse_180_start + t_180
	echo_time = pulse_180_end + te / 2
	end_time = echo_time + max(te / 2, 0.1)
	time = np.arange(int(np.floor(end_time / dt)) + 1, dtype=float) * dt

	mz = np.zeros_like(time)
	mxy = np.zeros_like(time)

	# Apply the 90° excitation over its specified duration.
	in_90 = time <= t_90
	angle_90 = (np.pi / 2) * np.clip(time[in_90] / t_90, 0.0, 1.0)
	mz[in_90] = np.cos(angle_90)
	mxy[in_90] = np.sin(angle_90)

	# Model reversible dephasing with an exponential envelope (a Lorentzian
	# off-resonance distribution). The 180° pulse reverses phase spread around
	# its center, while irreversible T2 decay continues throughout.
	after_90 = time > t_90
	pulse_180_center = (pulse_180_start + pulse_180_end) / 2
	elapsed = time[after_90] - t_90
	dephasing_time = np.where(
		time[after_90] <= pulse_180_center,
		elapsed,
		2 * (pulse_180_center - t_90) - elapsed,
	)
	t2_star = t2 / 2
	mxy[after_90] = (
		np.exp(-elapsed / t2)
		* np.exp(-np.abs(dephasing_time) / t2_star)
	)

	pulse_180_start_mz = 1.0 - np.exp(-(pulse_180_start - t_90) / t1)
	before_180 = (time > t_90) & (time < pulse_180_start)
	mz[before_180] = 1.0 - np.exp(-(time[before_180] - t_90) / t1)

	# Rotate the available magnetization around +Mx. With this RF convention,
	# +Mz tips toward +My and +My rotates toward -Mz.
	in_180 = (time >= pulse_180_start) & (time <= pulse_180_end)
	angle_180 = np.pi * np.clip(
		(time[in_180] - pulse_180_start) / t_180, 0.0, 1.0
	)
	my_at_pulse_start = np.interp(pulse_180_start, time, mxy)
	mz[in_180] = (
		pulse_180_start_mz * np.cos(angle_180)
		- my_at_pulse_start * np.sin(angle_180)
	)
	mz_after_180 = -pulse_180_start_mz

	# After the pulse, T1 recovery starts from the inverted magnetization.
	after_180 = time > pulse_180_end
	mz[after_180] = 1.0 + (mz_after_180 - 1.0) * np.exp(
		-(time[after_180] - pulse_180_end) / t1
	)

	my = mxy.copy()
	my[in_180] = (
		my_at_pulse_start * np.cos(angle_180)
		+ pulse_180_start_mz * np.sin(angle_180)
	)
	my[time > pulse_180_end] *= -1

	return pd.DataFrame(
		{
			"Time": time,
			"Mx": np.zeros_like(time),
			"My": my,
			"Mz": mz,
			"Mxy_net": mxy,
		}
	)
