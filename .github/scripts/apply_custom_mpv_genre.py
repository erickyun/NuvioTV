from pathlib import Path


def read(path: str) -> str:
    return Path(path).read_text()


def write(path: str, text: str) -> None:
    Path(path).write_text(text)


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected anchor once, found {count}: {old[:140]!r}")
    write(path, text.replace(old, new, 1))


def replace_all(path: str, old: str, new: str, expected: int) -> None:
    text = read(path)
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{path}: expected anchor {expected} times, found {count}: {old[:140]!r}")
    write(path, text.replace(old, new))


def create_new(path: str, text: str) -> None:
    target = Path(path)
    if target.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


# -----------------------------------------------------------------------------
# Device-local MPV video processing model
# -----------------------------------------------------------------------------
create_new(
    "app/src/main/java/com/nuvio/tv/data/local/MpvVideoProcessingSettings.kt",
    '''package com.nuvio.tv.data.local

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
'''
)


# -----------------------------------------------------------------------------
# PlayerSettingsDataStore: append device-local preferences without replacing any
# existing player setting.
# -----------------------------------------------------------------------------
p = "app/src/main/java/com/nuvio/tv/data/local/PlayerSettingsDataStore.kt"
replace_once(
    p,
    '''    val mpvHardwareDecodeMode: MpvHardwareDecodeMode = MpvHardwareDecodeMode.AUTO_SAFE,
    // Display settings''',
    '''    val mpvHardwareDecodeMode: MpvHardwareDecodeMode = MpvHardwareDecodeMode.AUTO_SAFE,
    val mpvVideoProcessing: MpvVideoProcessingSettings = MpvVideoProcessingSettings(),
    // Display settings'''
)
replace_once(
    p,
    '''    private val mpvHardwareDecodeModeKey = stringPreferencesKey("mpv_hardware_decode_mode")
    private val frameRateMatchingKey = booleanPreferencesKey("frame_rate_matching")''',
    '''    private val mpvHardwareDecodeModeKey = stringPreferencesKey("mpv_hardware_decode_mode")
    private val mpvDebandEnabledKey = booleanPreferencesKey("mpv_deband_enabled")
    private val mpvDebandIterationsKey = intPreferencesKey("mpv_deband_iterations")
    private val mpvDebandThresholdKey = intPreferencesKey("mpv_deband_threshold")
    private val mpvDebandRangeKey = intPreferencesKey("mpv_deband_range")
    private val mpvDebandGrainKey = intPreferencesKey("mpv_deband_grain")
    private val mpvDitherEnabledKey = booleanPreferencesKey("mpv_dither_enabled")
    private val mpvDitherModeKey = intPreferencesKey("mpv_dither_mode")
    private val mpvDitherDepthKey = intPreferencesKey("mpv_dither_depth")
    private val mpvErrorDiffusionKernelKey = intPreferencesKey("mpv_error_diffusion_kernel")
    private val frameRateMatchingKey = booleanPreferencesKey("frame_rate_matching")'''
)
replace_once(
    p,
    '''                mpvHardwareDecodeMode = parseMpvHardwareDecodeMode(prefs[mpvHardwareDecodeModeKey]),
                frameRateMatchingMode = prefs[frameRateMatchingModeKey]?.let {''',
    '''                mpvHardwareDecodeMode = parseMpvHardwareDecodeMode(prefs[mpvHardwareDecodeModeKey]),
                mpvVideoProcessing = MpvVideoProcessingSettings(
                    debandEnabled = prefs[mpvDebandEnabledKey] ?: false,
                    debandIterations = (prefs[mpvDebandIterationsKey]
                        ?: MpvVideoProcessingSettings.DEFAULT_DEBAND_ITERATIONS).coerceIn(
                        MpvVideoProcessingSettings.MIN_DEBAND_ITERATIONS,
                        MpvVideoProcessingSettings.MAX_DEBAND_ITERATIONS
                    ),
                    debandThreshold = (prefs[mpvDebandThresholdKey]
                        ?: MpvVideoProcessingSettings.DEFAULT_DEBAND_THRESHOLD).coerceIn(
                        MpvVideoProcessingSettings.MIN_DEBAND_THRESHOLD,
                        MpvVideoProcessingSettings.MAX_DEBAND_THRESHOLD
                    ),
                    debandRange = (prefs[mpvDebandRangeKey]
                        ?: MpvVideoProcessingSettings.DEFAULT_DEBAND_RANGE).coerceIn(
                        MpvVideoProcessingSettings.MIN_DEBAND_RANGE,
                        MpvVideoProcessingSettings.MAX_DEBAND_RANGE
                    ),
                    debandGrain = (prefs[mpvDebandGrainKey]
                        ?: MpvVideoProcessingSettings.DEFAULT_DEBAND_GRAIN).coerceIn(
                        MpvVideoProcessingSettings.MIN_DEBAND_GRAIN,
                        MpvVideoProcessingSettings.MAX_DEBAND_GRAIN
                    ),
                    ditherEnabled = prefs[mpvDitherEnabledKey] ?: false,
                    ditherMode = (prefs[mpvDitherModeKey]
                        ?: MpvVideoProcessingSettings.DITHER_MODE_ERROR_DIFFUSION).coerceIn(
                        MpvVideoProcessingSettings.MIN_DITHER_MODE,
                        MpvVideoProcessingSettings.MAX_DITHER_MODE
                    ),
                    ditherDepth = (prefs[mpvDitherDepthKey]
                        ?: MpvVideoProcessingSettings.DITHER_DEPTH_AUTO).let { stored ->
                        stored.takeIf { it in MpvVideoProcessingSettings.DITHER_DEPTH_VALUES }
                            ?: MpvVideoProcessingSettings.DITHER_DEPTH_AUTO
                    },
                    errorDiffusionKernel = (prefs[mpvErrorDiffusionKernelKey]
                        ?: MpvVideoProcessingSettings.ERROR_DIFFUSION_SIERRA_LITE).coerceIn(
                        MpvVideoProcessingSettings.MIN_ERROR_DIFFUSION_KERNEL,
                        MpvVideoProcessingSettings.MAX_ERROR_DIFFUSION_KERNEL
                    )
                ),
                frameRateMatchingMode = prefs[frameRateMatchingModeKey]?.let {'''
)
replace_once(
    p,
    '''    suspend fun setMpvHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        store().edit { prefs ->
            prefs[mpvHardwareDecodeModeKey] = mode.name
        }
    }

    /**
     * Set whether to use libass for ASS/SSA subtitle rendering
     */''',
    '''    suspend fun setMpvHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        store().edit { prefs ->
            prefs[mpvHardwareDecodeModeKey] = mode.name
        }
    }

    suspend fun setMpvDebandEnabled(enabled: Boolean) {
        store().edit { it[mpvDebandEnabledKey] = enabled }
    }

    suspend fun setMpvDebandIterations(value: Int) {
        store().edit {
            it[mpvDebandIterationsKey] = value.coerceIn(
                MpvVideoProcessingSettings.MIN_DEBAND_ITERATIONS,
                MpvVideoProcessingSettings.MAX_DEBAND_ITERATIONS
            )
        }
    }

    suspend fun setMpvDebandThreshold(value: Int) {
        store().edit {
            it[mpvDebandThresholdKey] = value.coerceIn(
                MpvVideoProcessingSettings.MIN_DEBAND_THRESHOLD,
                MpvVideoProcessingSettings.MAX_DEBAND_THRESHOLD
            )
        }
    }

    suspend fun setMpvDebandRange(value: Int) {
        store().edit {
            it[mpvDebandRangeKey] = value.coerceIn(
                MpvVideoProcessingSettings.MIN_DEBAND_RANGE,
                MpvVideoProcessingSettings.MAX_DEBAND_RANGE
            )
        }
    }

    suspend fun setMpvDebandGrain(value: Int) {
        store().edit {
            it[mpvDebandGrainKey] = value.coerceIn(
                MpvVideoProcessingSettings.MIN_DEBAND_GRAIN,
                MpvVideoProcessingSettings.MAX_DEBAND_GRAIN
            )
        }
    }

    suspend fun setMpvDitherEnabled(enabled: Boolean) {
        store().edit { it[mpvDitherEnabledKey] = enabled }
    }

    suspend fun setMpvDitherMode(value: Int) {
        store().edit {
            it[mpvDitherModeKey] = value.coerceIn(
                MpvVideoProcessingSettings.MIN_DITHER_MODE,
                MpvVideoProcessingSettings.MAX_DITHER_MODE
            )
        }
    }

    suspend fun setMpvDitherDepth(value: Int) {
        store().edit {
            it[mpvDitherDepthKey] = value.takeIf { it in MpvVideoProcessingSettings.DITHER_DEPTH_VALUES }
                ?: MpvVideoProcessingSettings.DITHER_DEPTH_AUTO
        }
    }

    suspend fun setMpvErrorDiffusionKernel(value: Int) {
        store().edit {
            it[mpvErrorDiffusionKernelKey] = value.coerceIn(
                MpvVideoProcessingSettings.MIN_ERROR_DIFFUSION_KERNEL,
                MpvVideoProcessingSettings.MAX_ERROR_DIFFUSION_KERNEL
            )
        }
    }

    /**
     * Set whether to use libass for ASS/SSA subtitle rendering
     */'''
)


# Keep new MPV preferences device-local, matching upstream mpv_hardware_decode_mode.
p = "app/src/main/java/com/nuvio/tv/core/sync/ProfileSettingsSyncService.kt"
replace_once(
    p,
    '''    "mpv_hardware_decode_mode",
    "frame_rate_matching",''',
    '''    "mpv_hardware_decode_mode",
    "mpv_deband_enabled",
    "mpv_deband_iterations",
    "mpv_deband_threshold",
    "mpv_deband_range",
    "mpv_deband_grain",
    "mpv_dither_enabled",
    "mpv_dither_mode",
    "mpv_dither_depth",
    "mpv_error_diffusion_kernel",
    "frame_rate_matching",'''
)


# -----------------------------------------------------------------------------
# Settings ViewModel and UI
# -----------------------------------------------------------------------------
p = "app/src/main/java/com/nuvio/tv/ui/screens/settings/PlaybackSettingsViewModel.kt"
replace_once(
    p,
    '''    suspend fun setMpvHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        playerSettingsDataStore.setMpvHardwareDecodeMode(mode)
    }


    suspend fun setDv5ToDv81Enabled(enabled: Boolean) {''',
    '''    suspend fun setMpvHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        playerSettingsDataStore.setMpvHardwareDecodeMode(mode)
    }

    suspend fun setMpvDebandEnabled(enabled: Boolean) = playerSettingsDataStore.setMpvDebandEnabled(enabled)
    suspend fun setMpvDebandIterations(value: Int) = playerSettingsDataStore.setMpvDebandIterations(value)
    suspend fun setMpvDebandThreshold(value: Int) = playerSettingsDataStore.setMpvDebandThreshold(value)
    suspend fun setMpvDebandRange(value: Int) = playerSettingsDataStore.setMpvDebandRange(value)
    suspend fun setMpvDebandGrain(value: Int) = playerSettingsDataStore.setMpvDebandGrain(value)
    suspend fun setMpvDitherEnabled(enabled: Boolean) = playerSettingsDataStore.setMpvDitherEnabled(enabled)
    suspend fun setMpvDitherMode(value: Int) = playerSettingsDataStore.setMpvDitherMode(value)
    suspend fun setMpvDitherDepth(value: Int) = playerSettingsDataStore.setMpvDitherDepth(value)
    suspend fun setMpvErrorDiffusionKernel(value: Int) = playerSettingsDataStore.setMpvErrorDiffusionKernel(value)

    suspend fun setDv5ToDv81Enabled(enabled: Boolean) {'''
)

create_new(
    "app/src/main/java/com/nuvio/tv/ui/screens/settings/PlaybackMpvVideoProcessingSettings.kt",
    '''package com.nuvio.tv.ui.screens.settings

import androidx.compose.foundation.lazy.LazyListScope
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Tune
import androidx.compose.ui.res.stringResource
import com.nuvio.tv.R
import com.nuvio.tv.data.local.InternalPlayerEngine
import com.nuvio.tv.data.local.MpvVideoProcessingSettings
import com.nuvio.tv.data.local.PlayerSettings

internal fun LazyListScope.mpvVideoProcessingSettingsItems(
    playerSettings: PlayerSettings,
    onSetDebandEnabled: (Boolean) -> Unit,
    onSetDebandIterations: (Int) -> Unit,
    onSetDebandThreshold: (Int) -> Unit,
    onSetDebandRange: (Int) -> Unit,
    onSetDebandGrain: (Int) -> Unit,
    onSetDitherEnabled: (Boolean) -> Unit,
    onSetDitherMode: (Int) -> Unit,
    onSetDitherDepth: (Int) -> Unit,
    onSetErrorDiffusionKernel: (Int) -> Unit,
    onItemFocused: () -> Unit = {},
    enabled: Boolean = true
) {
    val isMpvEngine = playerSettings.internalPlayerEngine == InternalPlayerEngine.MVP_PLAYER ||
        playerSettings.internalPlayerEngine == InternalPlayerEngine.AUTO
    if (!isMpvEngine) return

    val settings = playerSettings.mpvVideoProcessing

    item(key = "mpv_deband_enabled") {
        ToggleSettingsItem(
            icon = Icons.Default.Tune,
            title = stringResource(R.string.playback_mpv_deband_title),
            subtitle = stringResource(R.string.playback_mpv_deband_subtitle),
            isChecked = settings.debandEnabled,
            onCheckedChange = onSetDebandEnabled,
            onFocused = onItemFocused,
            enabled = enabled
        )
    }

    item(key = "mpv_deband_iterations") {
        SliderSettingsItem(
            icon = null,
            title = stringResource(R.string.playback_mpv_deband_iterations),
            value = settings.debandIterations,
            valueText = settings.debandIterations.toString(),
            minValue = MpvVideoProcessingSettings.MIN_DEBAND_ITERATIONS,
            maxValue = MpvVideoProcessingSettings.MAX_DEBAND_ITERATIONS,
            step = 1,
            onValueChange = onSetDebandIterations,
            subtitle = stringResource(R.string.playback_mpv_deband_iterations_subtitle),
            onFocused = onItemFocused,
            enabled = enabled && settings.debandEnabled
        )
    }

    item(key = "mpv_deband_threshold") {
        SliderSettingsItem(
            icon = null,
            title = stringResource(R.string.playback_mpv_deband_threshold),
            value = settings.debandThreshold,
            valueText = settings.debandThreshold.toString(),
            minValue = MpvVideoProcessingSettings.MIN_DEBAND_THRESHOLD,
            maxValue = MpvVideoProcessingSettings.MAX_DEBAND_THRESHOLD,
            step = 1,
            onValueChange = onSetDebandThreshold,
            subtitle = stringResource(R.string.playback_mpv_deband_threshold_subtitle),
            onFocused = onItemFocused,
            enabled = enabled && settings.debandEnabled
        )
    }

    item(key = "mpv_deband_range") {
        SliderSettingsItem(
            icon = null,
            title = stringResource(R.string.playback_mpv_deband_range),
            value = settings.debandRange,
            valueText = settings.debandRange.toString(),
            minValue = MpvVideoProcessingSettings.MIN_DEBAND_RANGE,
            maxValue = MpvVideoProcessingSettings.MAX_DEBAND_RANGE,
            step = 1,
            onValueChange = onSetDebandRange,
            subtitle = stringResource(R.string.playback_mpv_deband_range_subtitle),
            onFocused = onItemFocused,
            enabled = enabled && settings.debandEnabled
        )
    }

    item(key = "mpv_deband_grain") {
        SliderSettingsItem(
            icon = null,
            title = stringResource(R.string.playback_mpv_deband_grain),
            value = settings.debandGrain,
            valueText = settings.debandGrain.toString(),
            minValue = MpvVideoProcessingSettings.MIN_DEBAND_GRAIN,
            maxValue = MpvVideoProcessingSettings.MAX_DEBAND_GRAIN,
            step = 1,
            onValueChange = onSetDebandGrain,
            subtitle = stringResource(R.string.playback_mpv_deband_grain_subtitle),
            onFocused = onItemFocused,
            enabled = enabled && settings.debandEnabled
        )
    }

    item(key = "mpv_dither_enabled") {
        ToggleSettingsItem(
            icon = Icons.Default.Tune,
            title = stringResource(R.string.playback_mpv_dither_title),
            subtitle = stringResource(R.string.playback_mpv_dither_subtitle),
            isChecked = settings.ditherEnabled,
            onCheckedChange = onSetDitherEnabled,
            onFocused = onItemFocused,
            enabled = enabled
        )
    }

    item(key = "mpv_dither_mode") {
        SliderSettingsItem(
            icon = null,
            title = stringResource(R.string.playback_mpv_dither_mode),
            values = listOf(
                MpvVideoProcessingSettings.DITHER_MODE_FRUIT,
                MpvVideoProcessingSettings.DITHER_MODE_ORDERED,
                MpvVideoProcessingSettings.DITHER_MODE_ERROR_DIFFUSION
            ),
            selected = settings.ditherMode,
            valueText = when (settings.ditherMode) {
                MpvVideoProcessingSettings.DITHER_MODE_FRUIT -> stringResource(R.string.playback_mpv_dither_fruit)
                MpvVideoProcessingSettings.DITHER_MODE_ORDERED -> stringResource(R.string.playback_mpv_dither_ordered)
                else -> stringResource(R.string.playback_mpv_dither_error_diffusion)
            },
            onValueChange = onSetDitherMode,
            subtitle = stringResource(R.string.playback_mpv_dither_mode_subtitle),
            onFocused = onItemFocused,
            enabled = enabled && settings.ditherEnabled
        )
    }

    item(key = "mpv_dither_depth") {
        SliderSettingsItem(
            icon = null,
            title = stringResource(R.string.playback_mpv_dither_depth),
            values = MpvVideoProcessingSettings.DITHER_DEPTH_VALUES,
            selected = settings.ditherDepth,
            valueText = if (settings.ditherDepth == MpvVideoProcessingSettings.DITHER_DEPTH_AUTO) {
                stringResource(R.string.playback_mpv_dither_depth_auto)
            } else {
                stringResource(R.string.playback_mpv_dither_depth_bits, settings.ditherDepth)
            },
            onValueChange = onSetDitherDepth,
            subtitle = stringResource(R.string.playback_mpv_dither_depth_subtitle),
            onFocused = onItemFocused,
            enabled = enabled && settings.ditherEnabled
        )
    }

    item(key = "mpv_error_diffusion_kernel") {
        SliderSettingsItem(
            icon = null,
            title = stringResource(R.string.playback_mpv_error_diffusion_kernel),
            values = listOf(
                MpvVideoProcessingSettings.ERROR_DIFFUSION_SIMPLE,
                MpvVideoProcessingSettings.ERROR_DIFFUSION_SIERRA_LITE,
                MpvVideoProcessingSettings.ERROR_DIFFUSION_FLOYD_STEINBERG,
                MpvVideoProcessingSettings.ERROR_DIFFUSION_ATKINSON,
                MpvVideoProcessingSettings.ERROR_DIFFUSION_BURKES
            ),
            selected = settings.errorDiffusionKernel,
            valueText = when (settings.errorDiffusionKernel) {
                MpvVideoProcessingSettings.ERROR_DIFFUSION_SIMPLE -> "Simple"
                MpvVideoProcessingSettings.ERROR_DIFFUSION_FLOYD_STEINBERG -> "Floyd-Steinberg"
                MpvVideoProcessingSettings.ERROR_DIFFUSION_ATKINSON -> "Atkinson"
                MpvVideoProcessingSettings.ERROR_DIFFUSION_BURKES -> "Burkes"
                else -> "Sierra Lite"
            },
            onValueChange = onSetErrorDiffusionKernel,
            subtitle = stringResource(R.string.playback_mpv_error_diffusion_kernel_subtitle),
            onFocused = onItemFocused,
            enabled = enabled && settings.ditherEnabled &&
                settings.ditherMode == MpvVideoProcessingSettings.DITHER_MODE_ERROR_DIFFUSION
        )
    }
}
'''
)

p = "app/src/main/java/com/nuvio/tv/ui/screens/settings/PlaybackSettingsSections.kt"
replace_once(
    p,
    '''    onShowMpvHardwareDecodeModeDialog: () -> Unit,
    onShowLanguageDialog: () -> Unit,''',
    '''    onShowMpvHardwareDecodeModeDialog: () -> Unit,
    onSetMpvDebandEnabled: (Boolean) -> Unit,
    onSetMpvDebandIterations: (Int) -> Unit,
    onSetMpvDebandThreshold: (Int) -> Unit,
    onSetMpvDebandRange: (Int) -> Unit,
    onSetMpvDebandGrain: (Int) -> Unit,
    onSetMpvDitherEnabled: (Boolean) -> Unit,
    onSetMpvDitherMode: (Int) -> Unit,
    onSetMpvDitherDepth: (Int) -> Unit,
    onSetMpvErrorDiffusionKernel: (Int) -> Unit,
    onShowLanguageDialog: () -> Unit,'''
)
replace_once(
    p,
    '''                videoExtraItems = {
                    item(key = "general_afr_header") {''',
    '''                videoExtraItems = {
                    mpvVideoProcessingSettingsItems(
                        playerSettings = playerSettings,
                        onSetDebandEnabled = onSetMpvDebandEnabled,
                        onSetDebandIterations = onSetMpvDebandIterations,
                        onSetDebandThreshold = onSetMpvDebandThreshold,
                        onSetDebandRange = onSetMpvDebandRange,
                        onSetDebandGrain = onSetMpvDebandGrain,
                        onSetDitherEnabled = onSetMpvDitherEnabled,
                        onSetDitherMode = onSetMpvDitherMode,
                        onSetDitherDepth = onSetMpvDitherDepth,
                        onSetErrorDiffusionKernel = onSetMpvErrorDiffusionKernel,
                        onItemFocused = { focusedSection = PlaybackSection.AUDIO_TRAILER },
                        enabled = !generalUi.isExternalPlayer
                    )

                    item(key = "general_afr_header") {'''
)

p = "app/src/main/java/com/nuvio/tv/ui/screens/settings/PlaybackSettingsScreen.kt"
replace_once(
    p,
    '''                onShowMpvHardwareDecodeModeDialog = { openDialog { showMpvHardwareDecodeModeDialog = true } },
                onShowLanguageDialog = { openDialog { showLanguageDialog = true } },''',
    '''                onShowMpvHardwareDecodeModeDialog = { openDialog { showMpvHardwareDecodeModeDialog = true } },
                onSetMpvDebandEnabled = { value -> coroutineScope.launch { viewModel.setMpvDebandEnabled(value) } },
                onSetMpvDebandIterations = { value -> coroutineScope.launch { viewModel.setMpvDebandIterations(value) } },
                onSetMpvDebandThreshold = { value -> coroutineScope.launch { viewModel.setMpvDebandThreshold(value) } },
                onSetMpvDebandRange = { value -> coroutineScope.launch { viewModel.setMpvDebandRange(value) } },
                onSetMpvDebandGrain = { value -> coroutineScope.launch { viewModel.setMpvDebandGrain(value) } },
                onSetMpvDitherEnabled = { value -> coroutineScope.launch { viewModel.setMpvDitherEnabled(value) } },
                onSetMpvDitherMode = { value -> coroutineScope.launch { viewModel.setMpvDitherMode(value) } },
                onSetMpvDitherDepth = { value -> coroutineScope.launch { viewModel.setMpvDitherDepth(value) } },
                onSetMpvErrorDiffusionKernel = { value -> coroutineScope.launch { viewModel.setMpvErrorDiffusionKernel(value) } },
                onShowLanguageDialog = { openDialog { showLanguageDialog = true } },'''
)


# -----------------------------------------------------------------------------
# libmpv application. Properties are applied after setMedia() initializes mpv.
# -----------------------------------------------------------------------------
p = "app/src/main/java/com/nuvio/tv/ui/screens/player/NuvioMpvSurfaceView.kt"
replace_once(
    p,
    '''import com.nuvio.tv.data.local.MpvHardwareDecodeMode
import com.nuvio.tv.data.local.SubtitleStyleSettings''',
    '''import com.nuvio.tv.data.local.MpvHardwareDecodeMode
import com.nuvio.tv.data.local.MpvVideoProcessingSettings
import com.nuvio.tv.data.local.SubtitleStyleSettings'''
)
replace_once(
    p,
    '''    fun applyHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        hardwareDecodeMode = mode
        if (!initialized) return
        runCatching {
            mpv.setPropertyString("hwdec", mode.toMpvHwdecValue())
        }.onFailure {
            Log.w(TAG, "Failed to apply mpv hardware decode mode ($mode): ${it.message}")
        }
    }

    fun setSubtitleDelayMs(delayMs: Int) {''',
    '''    fun applyHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        hardwareDecodeMode = mode
        if (!initialized) return
        runCatching {
            mpv.setPropertyString("hwdec", mode.toMpvHwdecValue())
        }.onFailure {
            Log.w(TAG, "Failed to apply mpv hardware decode mode ($mode): ${it.message}")
        }
    }

    fun applyVideoProcessingSettings(settings: MpvVideoProcessingSettings) {
        if (!initialized) return
        runCatching {
            mpv.setPropertyString("deband", if (settings.debandEnabled) "yes" else "no")
            mpv.setPropertyString("deband-iterations", settings.debandIterations.toString())
            mpv.setPropertyString("deband-threshold", settings.debandThreshold.toString())
            mpv.setPropertyString("deband-range", settings.debandRange.toString())
            mpv.setPropertyString("deband-grain", settings.debandGrain.toString())

            if (settings.ditherEnabled) {
                val ditherMode = when (settings.ditherMode) {
                    MpvVideoProcessingSettings.DITHER_MODE_FRUIT -> "fruit"
                    MpvVideoProcessingSettings.DITHER_MODE_ORDERED -> "ordered"
                    else -> "error-diffusion"
                }
                val ditherDepth = if (settings.ditherDepth == MpvVideoProcessingSettings.DITHER_DEPTH_AUTO) {
                    "auto"
                } else {
                    settings.ditherDepth.toString()
                }
                val errorDiffusion = when (settings.errorDiffusionKernel) {
                    MpvVideoProcessingSettings.ERROR_DIFFUSION_SIMPLE -> "simple"
                    MpvVideoProcessingSettings.ERROR_DIFFUSION_FLOYD_STEINBERG -> "floyd-steinberg"
                    MpvVideoProcessingSettings.ERROR_DIFFUSION_ATKINSON -> "atkinson"
                    MpvVideoProcessingSettings.ERROR_DIFFUSION_BURKES -> "burkes"
                    else -> "sierra-lite"
                }
                mpv.setPropertyString("dither-depth", ditherDepth)
                mpv.setPropertyString("dither", ditherMode)
                mpv.setPropertyString("error-diffusion", errorDiffusion)
            } else {
                mpv.setPropertyString("dither-depth", "no")
            }
        }.onFailure {
            Log.w(TAG, "Failed to apply mpv video processing settings: ${it.message}")
        }
    }

    fun setSubtitleDelayMs(delayMs: Int) {'''
)

p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeController.kt"
replace_once(
    p,
    '''import com.nuvio.tv.data.local.MpvHardwareDecodeMode
import com.nuvio.tv.data.local.NextEpisodeThresholdMode''',
    '''import com.nuvio.tv.data.local.MpvHardwareDecodeMode
import com.nuvio.tv.data.local.MpvVideoProcessingSettings
import com.nuvio.tv.data.local.NextEpisodeThresholdMode'''
)
replace_once(
    p,
    '''    internal var mpvHardwareDecodeModeSetting: MpvHardwareDecodeMode = MpvHardwareDecodeMode.AUTO_SAFE
    internal var mpvPreferredAudioLanguages: List<String> = emptyList()''',
    '''    internal var mpvHardwareDecodeModeSetting: MpvHardwareDecodeMode = MpvHardwareDecodeMode.AUTO_SAFE
    internal var mpvVideoProcessingSettings: MpvVideoProcessingSettings = MpvVideoProcessingSettings()
    internal var mpvPreferredAudioLanguages: List<String> = emptyList()'''
)

p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerInitialization.kt"
replace_once(
    p,
    '''            mpvHardwareDecodeModeSetting = playerSettings.mpvHardwareDecodeMode
            var effectiveInternalPlayerEngine = overrideInternalPlayerEngine ?: playerSettings.internalPlayerEngine''',
    '''            mpvHardwareDecodeModeSetting = playerSettings.mpvHardwareDecodeMode
            mpvVideoProcessingSettings = playerSettings.mpvVideoProcessing
            var effectiveInternalPlayerEngine = overrideInternalPlayerEngine ?: playerSettings.internalPlayerEngine'''
)

p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerMpv.kt"
replace_all(
    p,
    '''        view.setMedia(currentStreamUrl, currentHeaders)
        view.setPlaybackSpeed(_uiState.value.playbackSpeed)''',
    '''        view.setMedia(currentStreamUrl, currentHeaders)
        view.applyVideoProcessingSettings(mpvVideoProcessingSettings)
        view.setPlaybackSpeed(_uiState.value.playbackSpeed)''',
    1
)
replace_all(
    p,
    '''        view.setMedia(url, headers, initialResumePosition)
        playbackAnalyticsDiagnostics.setStartupStartPosition(initialResumePosition)''',
    '''        view.setMedia(url, headers, initialResumePosition)
        view.applyVideoProcessingSettings(mpvVideoProcessingSettings)
        playbackAnalyticsDiagnostics.setStartupStartPosition(initialResumePosition)''',
    1
)

p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerObservers.kt"
replace_once(
    p,
    '''            val previousMpvHardwareDecodeMode = mpvHardwareDecodeModeSetting
            mpvHardwareDecodeModeSetting = settings.mpvHardwareDecodeMode
            if (isUsingMpvEngine() && previousMpvHardwareDecodeMode != mpvHardwareDecodeModeSetting) {
                mpvView?.applyHardwareDecodeMode(mpvHardwareDecodeModeSetting)
            }

            val resolvedAudioLanguages = resolvePreferredAudioLanguages(''',
    '''            val previousMpvHardwareDecodeMode = mpvHardwareDecodeModeSetting
            mpvHardwareDecodeModeSetting = settings.mpvHardwareDecodeMode
            if (isUsingMpvEngine() && previousMpvHardwareDecodeMode != mpvHardwareDecodeModeSetting) {
                mpvView?.applyHardwareDecodeMode(mpvHardwareDecodeModeSetting)
            }

            val previousMpvVideoProcessingSettings = mpvVideoProcessingSettings
            mpvVideoProcessingSettings = settings.mpvVideoProcessing
            if (isUsingMpvEngine() && previousMpvVideoProcessingSettings != mpvVideoProcessingSettings) {
                mpvView?.applyVideoProcessingSettings(mpvVideoProcessingSettings)
            }

            val resolvedAudioLanguages = resolvePreferredAudioLanguages('''
)


# -----------------------------------------------------------------------------
# Genre rows in the existing startup warning overlay. Existing parental warnings
# are left intact and are simply rendered after genre rows.
# -----------------------------------------------------------------------------
p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerUiState.kt"
replace_once(
    p,
    '''    val castMembers: List<MetaCastMember> = emptyList(),
    val showControls: Boolean = true,''',
    '''    val castMembers: List<MetaCastMember> = emptyList(),
    val genres: List<String> = emptyList(),
    val showControls: Boolean = true,'''
)

p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerMetadata.kt"
replace_once(
    p,
    '''        state.copy(
            description = description ?: state.description,
            castMembers = if (meta.castMembers.isNotEmpty()) meta.castMembers else state.castMembers,
            isNextEpisodeMetadataResolved = true
        )
    }
}''',
    '''        state.copy(
            description = description ?: state.description,
            castMembers = if (meta.castMembers.isNotEmpty()) meta.castMembers else state.castMembers,
            genres = meta.genres.map { it.trim() }.filter { it.isNotBlank() }.distinct(),
            isNextEpisodeMetadataResolved = true
        )
    }

    if (_uiState.value.isPlaying) {
        tryShowParentalGuide()
    }
}'''
)
replace_once(
    p,
    '''    if (!state.parentalGuideHasShown && state.parentalWarnings.isNotEmpty() && !playbackStartedForParentalGuide) {''',
    '''    if (!state.parentalGuideHasShown &&
        (state.parentalWarnings.isNotEmpty() || state.genres.isNotEmpty()) &&
        !playbackStartedForParentalGuide
    ) {'''
)

p = "app/src/main/java/com/nuvio/tv/ui/screens/player/ParentalGuideOverlay.kt"
replace_once(
    p,
    '''fun ParentalGuideOverlay(
    warnings: List<ParentalWarning>,
    isVisible: Boolean,
    onAnimationComplete: () -> Unit,
    modifier: Modifier = Modifier
) {
    if (warnings.isEmpty()) return

    val count = warnings.size''',
    '''fun ParentalGuideOverlay(
    warnings: List<ParentalWarning>,
    genres: List<String> = emptyList(),
    isVisible: Boolean,
    onAnimationComplete: () -> Unit,
    modifier: Modifier = Modifier
) {
    val displayWarnings = remember(warnings, genres) {
        genres
            .map { it.trim() }
            .filter { it.isNotBlank() }
            .distinct()
            .map { ParentalWarning(label = it, severity = "") } + warnings
    }
    if (displayWarnings.isEmpty()) return

    val count = displayWarnings.size'''
)
replace_once(
    p,
    '''            warnings.forEachIndexed { index, warning ->''',
    '''            displayWarnings.forEachIndexed { index, warning ->'''
)
replace_once(
    p,
    '''                    Text(
                        text = " · ",
                        fontSize = 11.sp,
                        color = Color.White.copy(alpha = 0.4f),
                    )
                    Text(
                        text = warning.severity,
                        fontSize = 11.sp,
                        color = Color.White.copy(alpha = 0.5f),
                    )''',
    '''                    if (warning.severity.isNotBlank()) {
                        Text(
                            text = " · ",
                            fontSize = 11.sp,
                            color = Color.White.copy(alpha = 0.4f),
                        )
                        Text(
                            text = warning.severity,
                            fontSize = 11.sp,
                            color = Color.White.copy(alpha = 0.5f),
                        )
                    }'''
)

p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerScreen.kt"
replace_once(
    p,
    '''        ParentalGuideOverlay(
            warnings = uiState.parentalWarnings,
            isVisible = uiState.showParentalGuide,''',
    '''        ParentalGuideOverlay(
            warnings = uiState.parentalWarnings,
            genres = uiState.genres,
            isVisible = uiState.showParentalGuide,'''
)


# -----------------------------------------------------------------------------
# New strings only. Existing translations/resources are untouched.
# -----------------------------------------------------------------------------
p = "app/src/main/res/values/strings.xml"
text = read(p)
marker = "</resources>"
if text.count(marker) != 1:
    raise SystemExit("strings.xml closing marker not unique")
additions = '''
    <!-- MPV video processing -->
    <string name="playback_mpv_deband_title">MPV Deband</string>
    <string name="playback_mpv_deband_subtitle">Reduce visible banding with mpv video processing.</string>
    <string name="playback_mpv_deband_iterations">Deband iterations</string>
    <string name="playback_mpv_deband_iterations_subtitle">mpv deband-iterations (0–16). Default: 1.</string>
    <string name="playback_mpv_deband_threshold">Deband threshold</string>
    <string name="playback_mpv_deband_threshold_subtitle">mpv deband-threshold (0–4096). Default: 48.</string>
    <string name="playback_mpv_deband_range">Deband range</string>
    <string name="playback_mpv_deband_range_subtitle">mpv deband-range (1–64). Default: 16.</string>
    <string name="playback_mpv_deband_grain">Deband grain</string>
    <string name="playback_mpv_deband_grain_subtitle">mpv deband-grain (0–4096). Default: 32.</string>
    <string name="playback_mpv_dither_title">MPV Dither</string>
    <string name="playback_mpv_dither_subtitle">Enable configurable mpv output dithering.</string>
    <string name="playback_mpv_dither_mode">Dither algorithm</string>
    <string name="playback_mpv_dither_mode_subtitle">Choose fruit, ordered, or error-diffusion dithering.</string>
    <string name="playback_mpv_dither_fruit">Fruit</string>
    <string name="playback_mpv_dither_ordered">Ordered</string>
    <string name="playback_mpv_dither_error_diffusion">Error diffusion</string>
    <string name="playback_mpv_dither_depth">Dither depth</string>
    <string name="playback_mpv_dither_depth_subtitle">Target output bit depth. Auto follows mpv display detection.</string>
    <string name="playback_mpv_dither_depth_auto">Auto</string>
    <string name="playback_mpv_dither_depth_bits">%1$d-bit</string>
    <string name="playback_mpv_error_diffusion_kernel">Error diffusion kernel</string>
    <string name="playback_mpv_error_diffusion_kernel_subtitle">Used when the dither algorithm is Error diffusion.</string>
'''
write(p, text.replace(marker, additions + marker, 1))

print("Custom MPV + genre patch applied")
