# CHZZK AirPlay Implementation Plan

> Implement using superpowers:executing-plans in the isolated clone.

**Goal:** CHZZK direct AirPlay video and audio on ARMv7 Fire TV.
**Architecture:** Normalize transport URI at player boundary, guard native stale-session handlers, separate music advertisement.
**Tech Stack:** Kotlin/Media3, JNI C/UxPlay, Gradle/Android NDK.
**Spec:** ../specs/2026-11-16-chzzk-airplay-design.md

## Constraints
Preserve upstream signing/data by using fork application ID. No credential-bearing fixtures. No DRM changes. Merge only after actual CHZZK AV verification.

## Review Focus
Encoded queries, malformed URI, FCUP loopback URLs, missing native playlist after stop, video/audio endpoint confusion.

## Tasks
- [x] Reproduce stale native request failure with synthetic HTTP replay on the device; add test script.
- [x] Add Kotlin regression tests for hlsurl HTTPS normalization, existing HTTP(S), encoded query preservation and malformed inputs; observe RED.
- [x] Implement media boundary handling and stale native guards; expose music advertisement option.
- [x] Run tests, lint and APK builds, inspect signed artifact, install ARMv7 fork.
- [ ] Run native replay, synthetic AV playback and real CHZZK direct AirPlay including reconnect.
- [ ] Review, commit, push, keep dependency PR open with a pinned pushed commit and merge app PR into fork main; verify remote state.

## Verification ledger
- URL tests: 3 RED failures before normalization; 4/4 GREEN afterward in both Debug and Release.
- Native guards: upstream stale action terminates receiver; fixed action/property/playlist tests return 400/400/404 and survive.
- Full Gradle test/lint/assemble: green; APK signatures verify, all three ABIs built.
- Synthetic hlsurl playback: ready, playing, position available on Fire TV.
- Final independent review: one P2 in device replay method/status expectations, corrected and device suite GREEN. No other actionable findings.
- Integration: user explicitly requested AirPlayer fork main merge; actual CHZZK AV test is still pending before merge.
