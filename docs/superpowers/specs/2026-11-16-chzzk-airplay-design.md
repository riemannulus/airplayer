# CHZZK direct AirPlay playback

The iPhone CHZZK AirPlay button must play video and audio on the Fire TV AFTKRT (Android 11, ARMv7), without screen mirroring. The Apple receiver comparison succeeds; current Android builds fail with an unrecognized hlsurl URI and then a missing-playlist native crash.

## Approach
Normalize the observed hlsurl wrapper to HTTPS at the media-player boundary, retaining authority, encoded path and query byte-for-byte. Keep existing HTTP(S)/local FCUP playback intact. Add bounded input handling and redacted diagnostic messages. Protect native request handlers from stale session state with a small patch in a fork of the existing UxPlay dependency. A dependency update alone does not handle the observed wrapper; replacing the receiver loses the requested open-source workflow.

Separate the optional music receiver advertisement from video reception so an iPhone cannot select the audio-only endpoint by mistake; the fork defaults to video reception and keeps music opt-in. No DRM changes, broadcast URLs, credentials or PINs enter repository fixtures or PRs.

## Validation
Failing unit cases for the actual URL-to-player boundary, including query preservation and existing HTTP(S). Device HTTP replay for stale /action and /setProperty after stop; repeat direct casting, reconnect and stop on the real Fire TV. Require the user to confirm CHZZK picture and sound before claiming end-to-end success and merging the app main. Test local synthetic AV media independently.

## Delivery
Fork repositories under riemannulus, implement on codex branches, review changes, pin the pushed dependency fix commit (dependency PR remains open) before updating app submodule, build and install a distinct fork application ID to avoid destroying the upstream installation or signing material, then merge tested app changes to fork main.
