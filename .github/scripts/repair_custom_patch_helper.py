from pathlib import Path

path = Path('.github/scripts/apply_custom_mpv_genre.py')
text = path.read_text()

old_anchor = """        view.setMedia(url, headers, initialResumePosition)
        playbackAnalyticsDiagnostics.setStartupStartPosition(initialResumePosition)"""
new_anchor = """        playbackAnalyticsDiagnostics.setStartupStartPosition(initialResumePosition)
        view.setMedia(url, headers, initialResumePosition)"""
old_replacement = """        view.setMedia(url, headers, initialResumePosition)
        view.applyVideoProcessingSettings(mpvVideoProcessingSettings)
        playbackAnalyticsDiagnostics.setStartupStartPosition(initialResumePosition)"""
new_replacement = """        playbackAnalyticsDiagnostics.setStartupStartPosition(initialResumePosition)
        view.setMedia(url, headers, initialResumePosition)
        view.applyVideoProcessingSettings(mpvVideoProcessingSettings)"""

if text.count(old_anchor) != 1:
    raise SystemExit(f'old MPV startup anchor count={text.count(old_anchor)}')
if text.count(old_replacement) != 1:
    raise SystemExit(f'old MPV startup replacement count={text.count(old_replacement)}')

text = text.replace(old_anchor, new_anchor, 1)
text = text.replace(old_replacement, new_replacement, 1)
path.write_text(text)
print('Patch helper aligned to latest upstream MPV startup order')
