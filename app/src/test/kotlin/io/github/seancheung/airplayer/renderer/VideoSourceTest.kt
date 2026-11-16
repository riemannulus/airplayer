package io.github.seancheung.airplayer.renderer

import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Test

class VideoSourceTest {
    @Test fun chzzkWrappedHlsUsesHttpsAndPreservesEncodedQuery() {
        assertEquals("https://cdn.example.test/live/channel_playlist.m3u8?key=a%2Fb%2Bc&quality=720&empty=",
            VideoSource.playbackUrl("hlsurl://cdn.example.test/live/channel_playlist.m3u8?key=a%2Fb%2Bc&quality=720&empty="))
    }
    @Test fun httpAndHttpsLocationsStayByteForByteUnchanged() {
        listOf("http://127.0.0.1:7000/master.m3u8", "https://cdn.example.test/video.mp4?key=a%2Fb+z").forEach {
            assertEquals(it, VideoSource.playbackUrl(it))
        }
    }
    @Test fun wrappedSchemeIsCaseInsensitive() {
        assertEquals("https://cdn.example.test/live.m3u8", VideoSource.playbackUrl("HLSURL://cdn.example.test/live.m3u8"))
    }
    @Test fun invalidOrUnsupportedLocationsAreRejectedWithoutLeakingTheirContents() {
        listOf("hlsurl:///live.m3u8", "hlsurl://", "file:///private/video", "not a URL", "https://cdn.example.test/bad path?secret=hidden").forEach {
            val error = assertThrows(IllegalArgumentException::class.java) { VideoSource.playbackUrl(it) }
            assertEquals("Unsupported or malformed AirPlay video URL", error.message)
        }
    }
}
