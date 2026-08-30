package com.nuvio.tv.data.local

/**
 * Device-local mpv video-processing preferences.
 *
 * Both processing stages are disabled by default so upstream Nuvio playback remains
 * unchanged until the user explicitly enables one of them.
 */
data class MpvVideoProcessingSettings(
    val debandEnabled: Boolean = false,
    val debandIterations: Int = DEFAULT_DEBAND_ITERATIONS,
    val debandThreshold: Int = DEFAULT_DEBAND_THRESHOLD,
    val debandRange: Int = DEFAULT_DEBAND_RANGE,
    val debandGrain: Int = DEFAULT_DEBAND_GRAIN,
    val ditherEnabled: Boolean = false,
    val ditherMode: Int = DITHER_MODE_ERROR_DIFFUSION,
    val ditherDepth: Int = DITHER_DEPTH_AUTO,
    val errorDiffusionKernel: Int = ERROR_DIFFUSION_SIERRA_LITE
) {
    companion object {
        const val MIN_DEBAND_ITERATIONS = 0
        const val MAX_DEBAND_ITERATIONS = 16
        const val DEFAULT_DEBAND_ITERATIONS = 1

        const val MIN_DEBAND_THRESHOLD = 0
        const val MAX_DEBAND_THRESHOLD = 4096
        const val DEFAULT_DEBAND_THRESHOLD = 48

        const val MIN_DEBAND_RANGE = 1
        const val MAX_DEBAND_RANGE = 64
        const val DEFAULT_DEBAND_RANGE = 16

        const val MIN_DEBAND_GRAIN = 0
        const val MAX_DEBAND_GRAIN = 4096
        const val DEFAULT_DEBAND_GRAIN = 32

        const val DITHER_MODE_FRUIT = 0
        const val DITHER_MODE_ORDERED = 1
        const val DITHER_MODE_ERROR_DIFFUSION = 2
        const val MIN_DITHER_MODE = DITHER_MODE_FRUIT
        const val MAX_DITHER_MODE = DITHER_MODE_ERROR_DIFFUSION

        const val DITHER_DEPTH_AUTO = 0
        val DITHER_DEPTH_VALUES = listOf(DITHER_DEPTH_AUTO, 8, 10, 12, 16)

        const val ERROR_DIFFUSION_SIMPLE = 0
        const val ERROR_DIFFUSION_SIERRA_LITE = 1
        const val ERROR_DIFFUSION_FLOYD_STEINBERG = 2
        const val ERROR_DIFFUSION_ATKINSON = 3
        const val ERROR_DIFFUSION_BURKES = 4
        const val MIN_ERROR_DIFFUSION_KERNEL = ERROR_DIFFUSION_SIMPLE
        const val MAX_ERROR_DIFFUSION_KERNEL = ERROR_DIFFUSION_BURKES
    }
}
