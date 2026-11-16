# CHZZK compatibility validation

## Changes

- Convert the observed iOS `hlsurl` playlist wrapper to HTTPS at the player boundary, retaining encoded paths and queries.
- Keep normal HTTP(S) and local FCUP playlist URLs intact.
- Reject late native action/property requests when there is no active video session; return explicitly framed empty responses.
- Make the additional audio-only Music receiver opt-in so video casting has a single default route.
- Install separately as `io.github.riemannulus.airplayer`, advertised as `Fire TV AirPlayer`.

## Automated and device evidence (2026-11-16)

- Before URL handling fix: 4 unit tests executed, 3 failures (hlsurl mapping, case-insensitive mapping, malformed/unsupported input rejection).
- After fix: Debug and Release unit suites each pass all 4 tests.
- `./gradlew test lintDebug assembleDebug`: successful. Existing dependency/deprecation lint warnings remain; no lint errors.
- Debug APK contains ARMv7, ARM64 and x86_64 libraries; APK v2 signature verifies.
- Device: Amazon AFTKRT, Android 11 / API 30, ARMv7.
- Upstream synthetic stale `/action` request closed the connection by terminating the app.
- Fixed receiver: stale POST `/action` returns 400; stale PUT `/setProperty?selectedMediaArray` returns 400; missing GET `/master.m3u8` returns 404. Process survives all three, and empty responses finish without waiting for disconnection.
- Apple's public HLS sample submitted as a synthetic `hlsurl` source reaches ready/playing state and reports a nonnegative position through `/playback-info`. The control socket stays open for the session, as required by UxPlay.
- Actual CHZZK iPhone AirPlay video/audio/reconnect check: pending user confirmation. Screen mirroring is not a substitute for this check.

The native dependency fix is pinned to a pushed commit in `riemannulus/UxPlay`; dependency PR https://github.com/riemannulus/UxPlay/pull/1 remains open. The submodule commit is reproducible without merging that separate repository's android branch.

No stream URLs, session credentials, authentication PINs, or private logs are included in fixtures or this report.
