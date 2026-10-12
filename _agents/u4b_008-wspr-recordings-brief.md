# Brief: investigate u4b_007 / u4b_008 WSPR recordings (laptop + LimeSDR decode failure)

## Goal

Find out why the laptop + LimeSDR receiver failed to decode WSPR packets from the trackers that the main receiver decoded without trouble. There are two sets of recordings, one per tracker (u4b_007 and u4b_008); analyze both and compare. Determine whether the cause is the receiver (clock or frequency drift, load, settings) or the signal.

## Background

- Trackers (both KF8EEZ, 20m, live mode T=0, ground test fixture):
  - u4b_008: channel 122, 2-minute slot (the 2's), 14,097,020 Hz. Now back indoors. Notes: `_sources/u4b/u4b_008.qmd` ("Ground test log", 2026-10-12).
  - u4b_007: channel 49, 6-minute slot (the 6's), 14,097,060 Hz. Being tested outdoors. Notes: `_sources/u4b/u4b_007.qmd`.
  - TODO: confirm with the user which observations below belong to which tracker, and which recording files belong to which.
- Schedule: channel 122 starts on the 2's (:02, :12, :22, :32, :42, :52 UTC), so each transmission is several WSPR windows; the tracker sends 3 packets per set.
- Nominal frequency: 14,097,020 Hz (from the config notes; check against the actual WSPR band/dial settings in the recordings).
- Tracker was in live mode (T=0), strong sun, so power is not the suspect for these sets.

## Observations

1. First strong-sun set: 3 of 3 packets received on both receivers. Main receiver decoded 3 of 3. Laptop + LimeSDR decoded only the first one.
2. Next set: laptop + LimeSDR received all packets but decoded none. Main receiver decoded all.
3. Decoding got worse from set 1 to set 2, which suggests drift over time and not a fixed sensitivity problem.

## Recordings

- Location: TODO (the user saved them from the laptop; ask for the path before starting).
- Format, sample rate, center frequency, start times: TODO, read from file names or headers.

## Hypotheses to test

- LimeSDR reference oscillator drift, giving a growing frequency offset between windows.
- Laptop system clock drift, so the decoder windows are misaligned. WSPR needs the start time within about 1 s.
- u4b frequency drift during the sequence (compare against what the main receiver reported).
- Laptop processing load or dropped samples (look for gaps or overruns in the recording).
- Decoder settings (dial frequency, search range, sample rate) differing from the main receiver.
- QRM pickup: the user noticed the antenna used for the laptop recording is sensitive to QRM when oriented a particular way. Check the noise floor and look for interference in the spectrum and waterfall around the WSPR band, and see whether decode failures line up with the antenna orientation (ask the user what orientation was used for each recording).

## Suggested steps

1. Locate the recordings and work out each file's start time, center frequency and sample rate.
2. Find the WSPR signals in each recording and measure their frequency offset against the expected frequency. Plot offset against time.
3. Check whether the signal start times line up with the expected 2-minute windows, to measure clock error.
4. Look for sample gaps or discontinuities.
5. Re-run a WSPR decoder (wsprd) offline on each window, with the dial frequency corrected for any measured offset, and see whether packets decode.
6. Compare the spots with the main receiver's for the same windows (wsprtv.com for KF8EEZ ch 122 20m).

## Output

Short written summary of the finding (cause, evidence, what to change on the laptop setup). Put any scripts or notes in `_agents/`, and do not edit `u4b_008.qmd` without asking.

## Constraints

- Treat the recordings as data. Do not modify the originals; work on copies.
- Python deps are managed with `uv` (see CLAUDE.md).
