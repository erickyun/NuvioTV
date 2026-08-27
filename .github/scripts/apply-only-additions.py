from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def patch(path: str, marker: str, old: str, new: str, expected: int = 1) -> None:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8")
    if marker in text:
        print(f"skip {path}: {marker}")
        return
    count = text.count(old)
    if count != expected:
        raise SystemExit(
            f"Refusing to patch {path}: expected {expected} occurrence(s), found {count} for anchor:\\n{old}"
        )
    text = text.replace(old, new, expected)
    file_path.write_text(text, encoding="utf-8")
    print(f"patched {path}")


# Player settings: additive persisted flags only.
patch(
    "app/src/main/java/com/nuvio/tv/data/local/PlayerSettingsDataStore.kt",
    "val mpvDebandEnabled: Boolean",
    '''    val mpvHardwareDecodeMode: MpvHardwareDecodeMode = MpvHardwareDecodeMode.AUTO_SAFE,
    // Display settings''',
    '''    val mpvHardwareDecodeMode: MpvHardwareDecodeMode = MpvHardwareDecodeMode.AUTO_SAFE,
    val mpvDebandEnabled: Boolean = false,
    val mpvDitherEnabled: Boolean = false,
    // Display settings''',
)
patch(
    "app/src/main/java/com/nuvio/tv/data/local/PlayerSettingsDataStore.kt",
    'mpvDebandEnabledKey = booleanPreferencesKey("mpv_deband_enabled")',
    '''    private val mpvHardwareDecodeModeKey = stringPreferencesKey("mpv_hardware_decode_mode")
    private val frameRateMatchingKey = booleanPreferencesKey("frame_rate_matching")''',
    '''    private val mpvHardwareDecodeModeKey = stringPreferencesKey("mpv_hardware_decode_mode")
    private val mpvDebandEnabledKey = booleanPreferencesKey("mpv_deband_enabled")
    private val mpvDitherEnabledKey = booleanPreferencesKey("mpv_dither_enabled")
    private val frameRateMatchingKey = booleanPreferencesKey("frame_rate_matching")''',
)
patch(
    "app/src/main/java/com/nuvio/tv/data/local/PlayerSettingsDataStore.kt",
    "mpvDebandEnabled = prefs[mpvDebandEnabledKey]",
    '''                mpvHardwareDecodeMode = parseMpvHardwareDecodeMode(prefs[mpvHardwareDecodeModeKey]),
                frameRateMatchingMode = prefs[frameRateMatchingModeKey]?.let {''',
    '''                mpvHardwareDecodeMode = parseMpvHardwareDecodeMode(prefs[mpvHardwareDecodeModeKey]),
                mpvDebandEnabled = prefs[mpvDebandEnabledKey] ?: false,
                mpvDitherEnabled = prefs[mpvDitherEnabledKey] ?: false,
                frameRateMatchingMode = prefs[frameRateMatchingModeKey]?.let {''',
)
patch(
    "app/src/main/java/com/nuvio/tv/data/local/PlayerSettingsDataStore.kt",
    "suspend fun setMpvDebandEnabled",
    '''    suspend fun setMpvHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        store().edit { prefs ->
            prefs[mpvHardwareDecodeModeKey] = mode.name
        }
    }
''',
    '''    suspend fun setMpvHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        store().edit { prefs ->
            prefs[mpvHardwareDecodeModeKey] = mode.name
        }
    }

    suspend fun setMpvDebandEnabled(enabled: Boolean) {
        store().edit { prefs ->
            prefs[mpvDebandEnabledKey] = enabled
        }
    }

    suspend fun setMpvDitherEnabled(enabled: Boolean) {
        store().edit { prefs ->
            prefs[mpvDitherEnabledKey] = enabled
        }
    }
''',
)

# Settings view model.
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/settings/PlaybackSettingsViewModel.kt",
    "suspend fun setMpvDebandEnabled",
    '''    suspend fun setMpvHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        playerSettingsDataStore.setMpvHardwareDecodeMode(mode)
    }
''',
    '''    suspend fun setMpvHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        playerSettingsDataStore.setMpvHardwareDecodeMode(mode)
    }

    suspend fun setMpvDebandEnabled(enabled: Boolean) {
        playerSettingsDataStore.setMpvDebandEnabled(enabled)
    }

    suspend fun setMpvDitherEnabled(enabled: Boolean) {
        playerSettingsDataStore.setMpvDitherEnabled(enabled)
    }
''',
)

# MPV video settings UI. Dither is intentionally immediately below Deband.
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/settings/PlaybackAudioSettings.kt",
    "onSetMpvDebandEnabled: (Boolean) -> Unit",
    '''    onShowMpvHardwareDecodeModeDialog: () -> Unit,
    onShowDv7HandlingModeDialog: () -> Unit,''',
    '''    onShowMpvHardwareDecodeModeDialog: () -> Unit,
    onSetMpvDebandEnabled: (Boolean) -> Unit,
    onSetMpvDitherEnabled: (Boolean) -> Unit,
    onShowDv7HandlingModeDialog: () -> Unit,''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/settings/PlaybackAudioSettings.kt",
    'item(key = "audio_mpv_deband")',
    '''        }
    }
}

@Composable
internal fun AudioSettingsDialogs(''',
    '''        }

        item(key = "audio_mpv_deband") {
            ToggleSettingsItem(
                icon = Icons.Default.Tune,
                title = stringResource(R.string.audio_mpv_deband_title),
                subtitle = stringResource(R.string.audio_mpv_deband_sub),
                isChecked = playerSettings.mpvDebandEnabled,
                onCheckedChange = onSetMpvDebandEnabled,
                onFocused = onItemFocused,
                enabled = enabled
            )
        }

        item(key = "audio_mpv_dither") {
            ToggleSettingsItem(
                icon = Icons.Default.Tune,
                title = stringResource(R.string.audio_mpv_dither_title),
                subtitle = stringResource(R.string.audio_mpv_dither_sub),
                isChecked = playerSettings.mpvDitherEnabled,
                onCheckedChange = onSetMpvDitherEnabled,
                onFocused = onItemFocused,
                enabled = enabled
            )
        }
    }
}

@Composable
internal fun AudioSettingsDialogs(''',
)

# Wire toggles through the settings screen without touching existing callbacks.
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/settings/PlaybackSettingsSections.kt",
    "onSetMpvDebandEnabled: (Boolean) -> Unit",
    '''    onShowMpvHardwareDecodeModeDialog: () -> Unit,
    onShowLanguageDialog: () -> Unit,''',
    '''    onShowMpvHardwareDecodeModeDialog: () -> Unit,
    onSetMpvDebandEnabled: (Boolean) -> Unit,
    onSetMpvDitherEnabled: (Boolean) -> Unit,
    onShowLanguageDialog: () -> Unit,''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/settings/PlaybackSettingsSections.kt",
    "onSetMpvDebandEnabled = onSetMpvDebandEnabled",
    '''                onShowMpvHardwareDecodeModeDialog = onShowMpvHardwareDecodeModeDialog,
                onShowDv7HandlingModeDialog = onShowDv7HandlingModeDialog,''',
    '''                onShowMpvHardwareDecodeModeDialog = onShowMpvHardwareDecodeModeDialog,
                onSetMpvDebandEnabled = onSetMpvDebandEnabled,
                onSetMpvDitherEnabled = onSetMpvDitherEnabled,
                onShowDv7HandlingModeDialog = onShowDv7HandlingModeDialog,''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/settings/PlaybackSettingsScreen.kt",
    "viewModel.setMpvDebandEnabled",
    '''                onShowMpvHardwareDecodeModeDialog = { openDialog { showMpvHardwareDecodeModeDialog = true } },
                onShowLanguageDialog = { openDialog { showLanguageDialog = true } },''',
    '''                onShowMpvHardwareDecodeModeDialog = { openDialog { showMpvHardwareDecodeModeDialog = true } },
                onSetMpvDebandEnabled = { enabled ->
                    coroutineScope.launch { viewModel.setMpvDebandEnabled(enabled) }
                },
                onSetMpvDitherEnabled = { enabled ->
                    coroutineScope.launch { viewModel.setMpvDitherEnabled(enabled) }
                },
                onShowLanguageDialog = { openDialog { showLanguageDialog = true } },''',
)

# Runtime state and live application.
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeController.kt",
    "mpvDebandEnabledSetting",
    '''    internal var mpvHardwareDecodeModeSetting: MpvHardwareDecodeMode = MpvHardwareDecodeMode.AUTO_SAFE
    internal var mpvPreferredAudioLanguages: List<String> = emptyList()''',
    '''    internal var mpvHardwareDecodeModeSetting: MpvHardwareDecodeMode = MpvHardwareDecodeMode.AUTO_SAFE
    internal var mpvDebandEnabledSetting: Boolean = false
    internal var mpvDitherEnabledSetting: Boolean = false
    internal var mpvPreferredAudioLanguages: List<String> = emptyList()''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerInitialization.kt",
    "mpvDebandEnabledSetting = playerSettings.mpvDebandEnabled",
    '''            mpvHardwareDecodeModeSetting = playerSettings.mpvHardwareDecodeMode
            var effectiveInternalPlayerEngine''',
    '''            mpvHardwareDecodeModeSetting = playerSettings.mpvHardwareDecodeMode
            mpvDebandEnabledSetting = playerSettings.mpvDebandEnabled
            mpvDitherEnabledSetting = playerSettings.mpvDitherEnabled
            var effectiveInternalPlayerEngine''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerObservers.kt",
    "previousMpvDebandEnabled",
    '''            if (isUsingMpvEngine() && previousMpvHardwareDecodeMode != mpvHardwareDecodeModeSetting) {
                mpvView?.applyHardwareDecodeMode(mpvHardwareDecodeModeSetting)
            }

            val resolvedAudioLanguages''',
    '''            if (isUsingMpvEngine() && previousMpvHardwareDecodeMode != mpvHardwareDecodeModeSetting) {
                mpvView?.applyHardwareDecodeMode(mpvHardwareDecodeModeSetting)
            }

            val previousMpvDebandEnabled = mpvDebandEnabledSetting
            val previousMpvDitherEnabled = mpvDitherEnabledSetting
            mpvDebandEnabledSetting = settings.mpvDebandEnabled
            mpvDitherEnabledSetting = settings.mpvDitherEnabled
            if (isUsingMpvEngine()) {
                if (previousMpvDebandEnabled != mpvDebandEnabledSetting) {
                    mpvView?.applyDebandEnabled(mpvDebandEnabledSetting)
                }
                if (previousMpvDitherEnabled != mpvDitherEnabledSetting) {
                    mpvView?.applyDitherEnabled(mpvDitherEnabledSetting)
                }
            }

            val resolvedAudioLanguages''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerMpv.kt",
    "view.applyDebandEnabled(mpvDebandEnabledSetting)",
    '''        view.applyHardwareDecodeMode(mpvHardwareDecodeModeSetting)
''',
    '''        view.applyHardwareDecodeMode(mpvHardwareDecodeModeSetting)
        view.applyDebandEnabled(mpvDebandEnabledSetting)
        view.applyDitherEnabled(mpvDitherEnabledSetting)
''',
    expected=2,
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerMpv.kt",
    "scheduleHideControls()\n        tryShowParentalGuide()",
    '''        scheduleHideControls()
        emitScrobbleStart()''',
    '''        scheduleHideControls()
        tryShowParentalGuide()
        emitScrobbleStart()''',
    expected=2,
)

# Actual libmpv properties. No other MPV property is changed.
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/NuvioMpvSurfaceView.kt",
    "fun applyDebandEnabled",
    '''    fun applyHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        hardwareDecodeMode = mode
        if (!initialized) return
        runCatching {
            mpv.setPropertyString("hwdec", mode.toMpvHwdecValue())
        }.onFailure {
            Log.w(TAG, "Failed to apply mpv hardware decode mode ($mode): ${it.message}")
        }
    }
''',
    '''    fun applyHardwareDecodeMode(mode: MpvHardwareDecodeMode) {
        hardwareDecodeMode = mode
        if (!initialized) return
        runCatching {
            mpv.setPropertyString("hwdec", mode.toMpvHwdecValue())
        }.onFailure {
            Log.w(TAG, "Failed to apply mpv hardware decode mode ($mode): ${it.message}")
        }
    }

    fun applyDebandEnabled(enabled: Boolean) {
        if (!initialized) return
        runCatching {
            mpv.setPropertyBoolean("deband", enabled)
        }.onFailure {
            Log.w(TAG, "Failed to apply mpv deband (enabled=$enabled): ${it.message}")
        }
    }

    fun applyDitherEnabled(enabled: Boolean) {
        if (!initialized) return
        runCatching {
            if (enabled) {
                mpv.setPropertyString("dither-depth", "auto")
                mpv.setPropertyString("dither", "error-diffusion")
                mpv.setPropertyString("error-diffusion", "sierra-lite")
            } else {
                mpv.setPropertyString("dither", "no")
            }
        }.onFailure {
            Log.w(TAG, "Failed to apply mpv dither (enabled=$enabled): ${it.message}")
        }
    }
''',
)

# Genre labels in the existing parental/content-warning overlay.
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerUiState.kt",
    "val parentalGenres: List<String>",
    '''    val parentalWarnings: List<ParentalWarning> = emptyList(),
    val showParentalGuide: Boolean = false,''',
    '''    val parentalWarnings: List<ParentalWarning> = emptyList(),
    val parentalGenres: List<String> = emptyList(),
    val showParentalGuide: Boolean = false,''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerMetadata.kt",
    "parentalGenres = meta.genres",
    '''            description = description ?: state.description,
            castMembers = if (meta.castMembers.isNotEmpty()) meta.castMembers else state.castMembers,
            isNextEpisodeMetadataResolved = true''',
    '''            description = description ?: state.description,
            castMembers = if (meta.castMembers.isNotEmpty()) meta.castMembers else state.castMembers,
            parentalGenres = meta.genres,
            isNextEpisodeMetadataResolved = true''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerMetadata.kt",
    "mpvView?.isPlayingNow() == true",
    '''    }
}

internal fun PlayerRuntimeController.resolveDescription(meta: Meta): String? {''',
    '''    }
    if (hasRenderedFirstFrame || (isUsingMpvEngine() && mpvView?.isPlayingNow() == true)) {
        tryShowParentalGuide()
    }
}

internal fun PlayerRuntimeController.resolveDescription(meta: Meta): String? {''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerMetadata.kt",
    "val hasParentalOverlayContent",
    '''internal fun PlayerRuntimeController.tryShowParentalGuide() {
    val state = _uiState.value
    if (!state.parentalGuideHasShown && state.parentalWarnings.isNotEmpty() && !playbackStartedForParentalGuide) {
        playbackStartedForParentalGuide = true
        _uiState.update { it.copy(showParentalGuide = true, parentalGuideHasShown = true) }
    }
}''',
    '''internal fun PlayerRuntimeController.tryShowParentalGuide() {
    if (!parentalGuideEnabled) return
    val state = _uiState.value
    val hasParentalOverlayContent =
        state.parentalWarnings.isNotEmpty() || state.parentalGenres.isNotEmpty()
    if (!state.parentalGuideHasShown && hasParentalOverlayContent && !playbackStartedForParentalGuide) {
        playbackStartedForParentalGuide = true
        _uiState.update { it.copy(showParentalGuide = true, parentalGuideHasShown = true) }
    }
}''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerScreen.kt",
    "genres = uiState.parentalGenres",
    '''                ParentalGuideOverlay(
                    warnings = uiState.parentalWarnings,
                    isVisible = uiState.showParentalGuide,''',
    '''                ParentalGuideOverlay(
                    warnings = uiState.parentalWarnings,
                    genres = uiState.parentalGenres,
                    isVisible = uiState.showParentalGuide,''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/ParentalGuideOverlay.kt",
    "genres: List<String>",
    '''fun ParentalGuideOverlay(
    warnings: List<ParentalWarning>,
    isVisible: Boolean,''',
    '''fun ParentalGuideOverlay(
    warnings: List<ParentalWarning>,
    genres: List<String> = emptyList(),
    isVisible: Boolean,''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/ParentalGuideOverlay.kt",
    "val entries = remember(genres, warnings)",
    '''    if (warnings.isEmpty()) return

    val count = warnings.size
    val totalLineHeight''',
    '''    val entries = remember(genres, warnings) {
        buildList<Pair<String, String?>>() {
            val seenGenres = mutableSetOf<String>()
            genres.forEach { rawGenre ->
                val genre = rawGenre.trim()
                if (genre.isNotBlank() && seenGenres.add(genre.lowercase())) {
                    add(genre to null)
                }
            }
            warnings.forEach { warning ->
                add(warning.label to warning.severity)
            }
        }
    }
    if (entries.isEmpty()) return

    val count = entries.size
    val totalLineHeight''',
)
patch(
    "app/src/main/java/com/nuvio/tv/ui/screens/player/ParentalGuideOverlay.kt",
    "entries.forEachIndexed",
    '''            warnings.forEachIndexed { index, warning ->
                Row(
                    modifier = Modifier
                        .height(ROW_HEIGHT)
                        .alpha(itemAlphas.getOrNull(index)?.value ?: 0f),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = warning.label,
                        fontSize = 11.sp,
                        color = Color.White.copy(alpha = 0.85f),
                        fontWeight = FontWeight.SemiBold
                    )
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
                }
            }''',
    '''            entries.forEachIndexed { index, entry ->
                Row(
                    modifier = Modifier
                        .height(ROW_HEIGHT)
                        .alpha(itemAlphas.getOrNull(index)?.value ?: 0f),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = entry.first,
                        fontSize = 11.sp,
                        color = Color.White.copy(alpha = 0.85f),
                        fontWeight = FontWeight.SemiBold
                    )
                    entry.second?.let { severity ->
                        Text(
                            text = " · ",
                            fontSize = 11.sp,
                            color = Color.White.copy(alpha = 0.4f),
                        )
                        Text(
                            text = severity,
                            fontSize = 11.sp,
                            color = Color.White.copy(alpha = 0.5f),
                        )
                    }
                }
            }''',
)

# Default-resource strings only; translations continue to fall back normally.
patch(
    "app/src/main/res/values/strings.xml",
    'name="audio_mpv_deband_title"',
    '''</resources>''',
    '''    <string name="audio_mpv_deband_title">MPV Deband</string>
    <string name="audio_mpv_deband_sub">Reduce visible color banding in gradients</string>
    <string name="audio_mpv_dither_title">MPV Dither</string>
    <string name="audio_mpv_dither_sub">Error-diffusion dithering (Sierra Lite)</string>
</resources>''',
)

print("All requested additive patches applied.")
