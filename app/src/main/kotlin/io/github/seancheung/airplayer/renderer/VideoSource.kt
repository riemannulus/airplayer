package io.github.seancheung.airplayer.renderer

import java.net.URI
import java.net.URISyntaxException

/** Resolves sender-side HLS wrappers without decoding signed paths or query parameters. */
internal object VideoSource {
    fun playbackUrl(location: String): String {
        val uri = try {
            URI(location)
        } catch (_: URISyntaxException) {
            throw invalidLocation()
        }
        if (uri.host.isNullOrBlank()) throw invalidLocation()
        return when (uri.scheme?.lowercase()) {
            // CHZZK's iOS player sends an HTTPS playlist behind this loader-specific scheme.
            "hlsurl" -> "https" + location.substring(location.indexOf(':'))
            "http", "https" -> location
            else -> throw invalidLocation()
        }
    }

    private fun invalidLocation() = IllegalArgumentException("Unsupported or malformed AirPlay video URL")
}
