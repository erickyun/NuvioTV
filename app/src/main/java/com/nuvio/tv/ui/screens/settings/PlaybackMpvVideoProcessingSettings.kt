package com.nuvio.tv.ui.screens.settings

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
