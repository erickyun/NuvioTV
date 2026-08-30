from pathlib import Path

UPSTREAM = "0a810f8bf4c70abffb3eb890e23733fe5b438901"


def read(path):
    return Path(path).read_text()


def write(path, text):
    Path(path).write_text(text)


def replace_once(path, old, new):
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one anchor, got {count}: {old[:100]!r}")
    write(path, text.replace(old, new, 1))


# PlayerUiState: keep existing custom `genres` addition, add independent visibility state/event.
p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerUiState.kt"
replace_once(
    p,
    "    val genres: List<String> = emptyList(),\n    val showControls: Boolean = true,",
    "    val genres: List<String> = emptyList(),\n    val showGenreGuide: Boolean = false,\n    val genreGuideHasShown: Boolean = false,\n    val showControls: Boolean = true,"
)
replace_once(
    p,
    "    data object OnParentalGuideHide : PlayerEvent()\n",
    "    data object OnParentalGuideHide : PlayerEvent()\n    data object OnGenreGuideHide : PlayerEvent()\n"
)

# Metadata: upstream file was restored before this script. Only insert new genre lines/functions.
p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerMetadata.kt"
replace_once(
    p,
    "    val description = resolveDescription(meta)\n\n    recomputeNextEpisode(resetVisibility = false)",
    "    val description = resolveDescription(meta)\n    val genres = meta.genres.map { it.trim() }.filter { it.isNotBlank() }.distinct()\n\n    recomputeNextEpisode(resetVisibility = false)"
)
replace_once(
    p,
    "            description = description ?: state.description,\n            castMembers = if (meta.castMembers.isNotEmpty()) meta.castMembers else state.castMembers,\n            isNextEpisodeMetadataResolved = true",
    "            description = description ?: state.description,\n            castMembers = if (meta.castMembers.isNotEmpty()) meta.castMembers else state.castMembers,\n            genres = genres,\n            showGenreGuide = if (genres != state.genres) false else state.showGenreGuide,\n            genreGuideHasShown = if (genres != state.genres) false else state.genreGuideHasShown,\n            isNextEpisodeMetadataResolved = true"
)
replace_once(
    p,
    "    }\n}\n\ninternal fun PlayerRuntimeController.resolveDescription(meta: Meta): String? {",
    "    }\n\n    if (hasRenderedFirstFrame || _uiState.value.isPlaying) {\n        tryShowGenreGuide()\n    }\n}\n\ninternal fun PlayerRuntimeController.resolveDescription(meta: Meta): String? {"
)
replace_once(
    p,
    "internal fun PlayerRuntimeController.tryShowParentalGuide() {\n    val state = _uiState.value\n    if (!state.parentalGuideHasShown && state.parentalWarnings.isNotEmpty() && !playbackStartedForParentalGuide) {\n        playbackStartedForParentalGuide = true\n        _uiState.update { it.copy(showParentalGuide = true, parentalGuideHasShown = true) }\n    }\n}\n",
    "internal fun PlayerRuntimeController.tryShowParentalGuide() {\n    val state = _uiState.value\n    if (!state.parentalGuideHasShown && state.parentalWarnings.isNotEmpty() && !playbackStartedForParentalGuide) {\n        playbackStartedForParentalGuide = true\n        _uiState.update { it.copy(showParentalGuide = true, parentalGuideHasShown = true) }\n    }\n}\n\ninternal fun PlayerRuntimeController.tryShowGenreGuide() {\n    val state = _uiState.value\n    if (!state.genreGuideHasShown && state.genres.isNotEmpty()) {\n        _uiState.update { it.copy(showGenreGuide = true, genreGuideHasShown = true) }\n    }\n}\n"
)

# Exo first frame: show genres next to the existing parental startup trigger.
p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerInitialization.kt"
text = read(p)
anchor = "                    tryShowParentalGuide()\n"
if text.count(anchor) != 1:
    raise SystemExit(f"{p}: tryShowParentalGuide anchor count={text.count(anchor)}")
write(p, text.replace(anchor, anchor + "                    tryShowGenreGuide()\n", 1))

# MPV first frame: trigger genre overlay once the first frame is genuinely ready.
p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerRuntimeControllerPlaybackEvents.kt"
replace_once(
    p,
    "                                hasRenderedFirstFrame = true\n                                val clickToFirstFrameMs = launchStartedAtElapsedMs",
    "                                hasRenderedFirstFrame = true\n                                tryShowGenreGuide()\n                                val clickToFirstFrameMs = launchStartedAtElapsedMs"
)
replace_once(
    p,
    "        PlayerEvent.OnParentalGuideHide -> {\n            _uiState.update { it.copy(showParentalGuide = false) }\n        }\n",
    "        PlayerEvent.OnParentalGuideHide -> {\n            _uiState.update { it.copy(showParentalGuide = false) }\n        }\n        PlayerEvent.OnGenreGuideHide -> {\n            _uiState.update { it.copy(showGenreGuide = false) }\n        }\n"
)

# PlayerScreen: upstream file was restored; append a separate genre overlay after parental overlay.
p = "app/src/main/java/com/nuvio/tv/ui/screens/player/PlayerScreen.kt"
parental_block = """        // Parental guide overlay (shows when video first starts playing)
        ParentalGuideOverlay(
            warnings = uiState.parentalWarnings,
            isVisible = uiState.showParentalGuide,
            onAnimationComplete = {
                viewModel.onEvent(PlayerEvent.OnParentalGuideHide)
            },
            modifier = Modifier.align(Alignment.TopStart)
        )
"""
genre_block = parental_block + """
        GenreGuideOverlay(
            genres = uiState.genres,
            warningCount = uiState.parentalWarnings.size,
            isVisible = uiState.showGenreGuide,
            onAnimationComplete = {
                viewModel.onEvent(PlayerEvent.OnGenreGuideHide)
            },
            modifier = Modifier.align(Alignment.TopStart)
        )
"""
replace_once(p, parental_block, genre_block)

# New standalone overlay. Existing ParentalGuideOverlay remains byte-for-byte upstream.
new_path = Path("app/src/main/java/com/nuvio/tv/ui/screens/player/GenreGuideOverlay.kt")
if new_path.exists():
    raise SystemExit(f"{new_path}: already exists")
new_path.write_text(r'''@file:OptIn(androidx.tv.material3.ExperimentalTvMaterial3Api::class)

package com.nuvio.tv.ui.screens.player

import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.tv.material3.Text
import com.nuvio.tv.ui.theme.NuvioTheme
import com.nuvio.tv.ui.theme.ThemeColors
import com.nuvio.tv.ui.theme.accentBrush
import kotlinx.coroutines.delay

private val GENRE_ROW_HEIGHT = 18.dp
private val GENRE_ROW_GAP = 2.dp

/**
 * Startup genre overlay. Kept separate from ParentalGuideOverlay so upstream
 * content-warning behavior remains completely unchanged.
 */
@Composable
fun GenreGuideOverlay(
    genres: List<String>,
    warningCount: Int,
    isVisible: Boolean,
    onAnimationComplete: () -> Unit,
    modifier: Modifier = Modifier
) {
    val displayGenres = remember(genres) {
        genres.map { it.trim() }
            .filter { it.isNotBlank() }
            .distinctBy { it.lowercase() }
    }
    if (displayGenres.isEmpty()) return

    val count = displayGenres.size
    val totalLineHeight = (GENRE_ROW_HEIGHT.value * count) + (GENRE_ROW_GAP.value * (count - 1))
    val accentBrush = ThemeColors.getColorPalette(NuvioTheme.currentTheme).accentBrush()
    val warningOffset = if (warningCount > 0) (22 * warningCount + 8).dp else 0.dp

    val containerAlpha = remember { Animatable(0f) }
    val lineHeightFraction = remember { Animatable(0f) }
    val itemAlphas = remember(count) { List(count) { Animatable(0f) } }
    var animating by remember { mutableStateOf(false) }

    LaunchedEffect(isVisible, displayGenres) {
        if (isVisible && !animating) {
            animating = true
            containerAlpha.animateTo(1f, tween(300))
            lineHeightFraction.animateTo(1f, tween(400, easing = FastOutSlowInEasing))
            for (i in 0 until count) {
                delay(80)
                itemAlphas[i].animateTo(1f, tween(200))
            }
            delay(5000)
            for (i in (count - 1) downTo 0) {
                delay(60)
                itemAlphas[i].animateTo(0f, tween(150))
            }
            delay(100)
            lineHeightFraction.animateTo(0f, tween(300, easing = FastOutSlowInEasing))
            delay(200)
            containerAlpha.animateTo(0f, tween(200))
            animating = false
            onAnimationComplete()
        } else if (!isVisible && animating) {
            for (i in (count - 1) downTo 0) itemAlphas[i].snapTo(0f)
            lineHeightFraction.snapTo(0f)
            containerAlpha.snapTo(0f)
            animating = false
            onAnimationComplete()
        }
    }

    if (containerAlpha.value <= 0f) return

    Row(
        modifier = modifier
            .alpha(containerAlpha.value)
            .padding(
                start = NuvioTheme.spacing.xxl,
                top = NuvioTheme.spacing.xl + warningOffset
            ),
        verticalAlignment = Alignment.Top
    ) {
        Box(
            modifier = Modifier
                .width(3.dp)
                .height((totalLineHeight * lineHeightFraction.value).dp)
                .clip(RoundedCornerShape(NuvioTheme.spacing.hairline))
                .background(accentBrush)
        )
        Column(
            modifier = Modifier.padding(start = 10.dp),
            verticalArrangement = Arrangement.spacedBy(GENRE_ROW_GAP)
        ) {
            displayGenres.forEachIndexed { index, genre ->
                Row(
                    modifier = Modifier
                        .height(GENRE_ROW_HEIGHT)
                        .alpha(itemAlphas.getOrNull(index)?.value ?: 0f),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = genre,
                        fontSize = 11.sp,
                        color = Color.White.copy(alpha = 0.85f),
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }
        }
    }
}
''')

print("additive genre overlay patch applied")
