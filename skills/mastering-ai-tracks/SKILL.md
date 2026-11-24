---
name: "mastering-ai-tracks"
description: "Master or edit AI-generated (Suno) tracks in Python: analysis, artifact removal, Owsinski/Katz-based chain, stem work, word fixes and section splices."
---

> Cópia da skill salva na conta (`anthropic-skills:mastering-ai-tracks`). Desde então o teto padrão passou para **−2 dBTP** (picos após codecs); ver `docs/02-masterizacao.md`.


# Mastering and editing AI-generated tracks (no DAW)

The user produces Brazilian tracks (pagode, funk, piseiro, rap, skate punk, ballads), mostly generated with Suno, and has no DAW. Reply in Portuguese. All work is done in Python (numpy, scipy, soundfile, pyloudnorm, librosa; faster-whisper for lyrics; ffmpeg for I/O). The assistant cannot listen: every judgement is a measurement, and the user's ears are the final judge. Report numbers in plain language and ask where something sounds wrong.

## Delivery standard
- 24-bit WAV (master), MP3 320 kbps (listening), and an `AB_matched` copy at the source's loudness for equal-loudness comparison (Katz).
- True peak -1 dBTP (Owsinski: online delivery). Note when the MP3 lands above -1 (fine for listening; upload the WAV).
- Keep the source sample rate; if stems arrive at another rate, resample the stems (soxr), never the original track.
- Verify with `ffmpeg -af ebur128=peak=true` (I, LRA, true peak).

## 1. Analyse before touching
- Integrated LUFS, true peak (4x oversampled), crest factor (100 ms windows), short-term LUFS profile (3 s), L/R correlation, side vs mid below 120 Hz, 1/3-octave spectrum.
- Section map: transcribe with faster-whisper (medium, language pt, word timestamps) to find verse/chorus/bridge.
- Artifact scan: stationary spectral lines (STFT N=16384, >8 dB over a 1/3-octave median in >50% of frames). Check pitch stability: lines that wander a few Hz or fall on note frequencies (e.g. 61.5 Hz bass, 495/659/987 Hz) are music; keep them.
- Known Suno artifacts: fixed 12,800 Hz tone; a ~850 Hz drone much stronger than in the mix; a comb of tones every ~100 Hz from ~16.9 to 20 kHz. Remove with a narrow spectral clamp (bins within +-6 to 12 Hz pulled down to the neighbourhood median, 2 passes, N=16384), then confirm the change below 15 kHz is >90 dB down.

## 2. Mastering chain (default)
1. HPF 25-28 Hz; M/S: side high-passed at 100 Hz (mono lows).
2. Low-end build-up (often 63 Hz in these mixes): static -1 to -1.5 dB plus a dynamic band (iirpeak, up to -2.5 dB on the loudest hits). Exception: if the 63 Hz energy is a surdo/kick that carries the groove (pagode), do not cut it.
3. Tonal EQ: gentle mid cuts where a hump exists (200, 250, 500 Hz); presence +1 to +2.5 dB around 3 kHz; air shelf +1.5 to +2.5 dB at 9-10 kHz. Be conservative on MP3 sources (codec artifacts).
4. Dynamic de-harsh: 2.5-5 kHz and 6-12 kHz bands, gain reduction only when the band exceeds the 500-2000 Hz reference by its 93rd-95th percentile; max 3 dB.
5. Glue: 1.5:1 (Katz range 1.5-3:1), slow-ish attack 30 ms, release 150-170 ms, about 1 dB on loud parts. For groove-driven music, high-pass the detector at 150 Hz so the surdo/kick does not trigger it.
6. Limiter: lookahead ~5 ms, minimum-filter envelope, release 40-80 ms. Rule (Owsinski): 99th percentile gain reduction <= 2-3 dB. Try targets (-11 to -14 LUFS) and pick the loudest that passes.
7. If peaks are too high for the target: add a fast transient stage (3 ms window, 8 ms release, threshold at the 99th percentile, max 4 dB) before the limiter (Katz: short transients tolerate 4-6 dB). Skip it when the track's groove depends on boosted transients.

Checks after rendering: tone change vs source by band; vocal-range index (1-4 kHz vs 150-1000 Hz on the mid) should not rise much more than ~1 dB (the user dislikes vocals pushed forward); crest factor and section loudness differences preserved (do not flatten intros/bridges unless asked); L/R correlation; mono behaviour.

## 3. Working from stems
- First test if the stems sum to the track (least-squares gains, residual). If the residual is very low (e.g. -69 dB), edits are exact arithmetic: `out = mix + w*(new - old)` inside the edited window, untouched elsewhere.
- If they do not sum (separated stems, residual around -3 to -16 dB), use per-bin NNLS power fit of vocal and instrumental, a Wiener mask with a -25 dB floor, and re-synthesis.
- Crowd/ambience in live recordings tends to sit in the `other` stem, wide and out of phase. Control it with M/S (lower side) and level envelopes rather than cutting it.
- Groove (pagode): transient shaper on the surdo band (attack +2.5, tail -2 dB), snap on 2-12 kHz percussion (+3 to +4 dB attack), parallel compression only above 150 Hz (ghost notes), chop attack on cavaco/violao. Bass gain is fine, but generate saturation harmonics only above 150 Hz or they fill the gaps between surdo hits. Measure surdo punch as the 95th minus the median of 10 ms frames in 45-120 Hz.

## 4. Word fixes and section splices
- Locate words with whisper; align fix takes locally (lag usually ~0); verify bit-identical samples outside the edit window.
- Cut only in shared pauses or consonants; check that pitch matches (within ~25 cents) if a crossfade must fall inside a voiced sound; keep crossfades short (20-120 ms).
- AI-regenerated takes can differ in stereo doubling (L/R correlation much lower than the original). If a fixed word sounds strange, check this, and prefer transplanting the same words from another chorus of the original singer (one chorus per channel recreates a natural double).
- Match loudness of the replaced word within +-0.3 LU and check band levels against how the same word sits in other choruses.
- Section removal: choruses are not sample-identical and the tempo drifts. Measure the lag by drum-hit coincidence (onsets in 40-120 Hz and 4-12 kHz within +-8 ms), section by section, not by broad envelope correlation (it can lock a 16th note off and make the result feel rushed). Splice in a shared vocal pause; use equal-power crossfades for uncorrelated takes.
- Then transcribe the whole result to confirm lyric order.

## 5. Adding a sample
- Measure the song tuning (librosa.estimate_tuning) and the sample's exact pitch in cents (pyin). Retune by the measured cents (resampling, no phase vocoder), aiming at a chord tone of the song's key.
- Place on downbeats (strongest kick phase), in instrumental gaps that end before the next vocal phrase; high-pass the sample (about 180 Hz) and set it about 2.5 LU under the section.

## Communication
- Lead with what changed and why, in plain Portuguese; give before/after numbers only where they help the user decide.
- Always offer A/B clips of the edited spots.
- When a choice is a trade-off (loudness vs limiting, bass vs surdo punch, crowd level), state it in one line and offer the alternative.