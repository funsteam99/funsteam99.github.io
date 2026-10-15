param([switch]$VerifyOnly)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$assetRoot = Join-Path $repo '../serial-assets'
$pythonExe = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
if (!(Test-Path -LiteralPath $pythonExe)) { $pythonExe = (Get-Command python -ErrorAction Stop).Source }
& $pythonExe -c 'import PIL'
if ($LASTEXITCODE -ne 0) { throw 'Python with Pillow required; refusing whole-page fallback' }
$nowTaipei = [TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow, 'Taipei Standard Time')
if (!$VerifyOnly) {
  if (git -C $repo status --porcelain) { throw 'Publishing checkout has uncommitted changes' }
  git -C $repo switch main
  if ($LASTEXITCODE -ne 0) { throw 'Unable to switch to main' }
  git -C $repo pull --ff-only origin main
  if ($LASTEXITCODE -ne 0) { throw 'Unable to update shared schedule from main' }
}
$schedule = Get-Content -LiteralPath (Join-Path $repo '_operations/publishing-schedule.md') -Raw
$section = [regex]::Match($schedule, '(?s)<!-- modern-journey-schedule:start -->(.*?)<!-- modern-journey-schedule:end -->')
if (!$section.Success) { throw 'Shared comic schedule missing; no fallback dates permitted' }
$episodes = @($section.Groups[1].Value -split '\r?\n' | ForEach-Object {
  if ($_ -match '^\|\s*\d{4}-') {
    $cells = @($_.Trim().Trim('|').Split('|') | ForEach-Object { $_.Trim() })
    if ($cells.Count -ne 6) { throw 'Invalid comic schedule row' }
    $due = [datetime]::ParseExact($cells[0], 'yyyy-MM-dd HH:mm', [Globalization.CultureInfo]::InvariantCulture)
    if ($cells[1] -notmatch '^0[2-8]$') { throw 'Unapproved episode number' }
    if ($cells[5] -ne 'Codex本機排程') { throw 'Comic executor mismatch; coordinate before publishing' }
    if ($cells[3] -ne "serial-assets/episode-$($cells[1]).png") { throw 'Unexpected comic asset path' }
    if (!(Test-Path -LiteralPath (Join-Path $assetRoot "episode-$($cells[1]).png"))) { throw 'Scheduled comic asset missing' }
    @{number=$cells[1]; date=$due.ToString('yyyy-MM-dd'); due=$due; title=$cells[2]; asset=$cells[3]; status=$cells[4]; width=$(if ($cells[1] -eq '02') {1536} else {1024}); height=$(if ($cells[1] -eq '02') {1024} else {1536})}
  }
})
if ($episodes.Count -eq 0) { throw 'Shared schedule contains no comic rows' }
if (@($episodes | Group-Object number | Where-Object Count -gt 1).Count -gt 0) { throw 'Duplicate comic episode in shared schedule' }
if (@($episodes | Group-Object { $_.due.Date.AddDays(-(([int]$_.due.DayOfWeek + 6) % 7)).ToString('yyyy-MM-dd') } | Where-Object Count -gt 1).Count -gt 0) { throw 'Multiple comic episodes in the same week' }
$page = Join-Path $repo 'modern-journey/index.html'
$html = Get-Content -LiteralPath $page -Raw
$changed = $false
foreach ($episode in $episodes) {
  $n = $episode.number
  $marker = "weekly-journey-ep$n"
  $existing = [regex]::Match($html, ('(?s)<article\b[^>]*\bid="' + [regex]::Escape($marker) + '"[^>]*>.*?</article>'))
  if ($existing.Success) {
    if (!$existing.Value.Contains("comic-reader.html id='journey-$n'")) { throw "Published episode requires panel repair: $marker" }
    continue
  }
  if ($episode.status.StartsWith('已發布')) { throw "Schedule says published but main marker is missing: $marker" }
  if ($episode.due -gt $nowTaipei) { continue }
  if ($VerifyOnly) { Write-Output "Due: $marker $($episode.due)"; continue }
  if (!$changed) {
    $publishBranch = 'codex/modern-journey-' + $nowTaipei.ToString('yyyyMMdd-HHmmss')
    git -C $repo switch -c $publishBranch
    if ($LASTEXITCODE -ne 0) { throw 'Unable to create publishing branch' }
  }
  & $pythonExe (Join-Path $repo 'scripts/prepare_scheduled_comic.py') --episode $n --title $episode.title --date $episode.date --source (Join-Path $assetRoot "episode-$n.png")
  if ($LASTEXITCODE -ne 0) { throw "Panel preparation failed for $marker; no whole-page fallback permitted" }
  $html = Get-Content -LiteralPath $page -Raw
  $changed = $true
}
if ($VerifyOnly) { Write-Output ('Verified shared comic schedule: ' + $episodes.Count + ' rows'); exit 0 }
if (!$changed) { Write-Output 'No unpublished episodes due'; exit 0 }
[IO.File]::WriteAllText($page, $html, [Text.UTF8Encoding]::new($false))
git -C $repo diff --check
if ($LASTEXITCODE -ne 0) { throw 'Diff validation failed' }
git -C $repo add -- modern-journey/index.html _data/journey_episodes.json _data/comic_panel_specs.json _data/comic_panels.json assets/images/panels assets/images/comics/weekly-journey-ep*.png
git -C $repo commit -m 'Publish scheduled Modern Journey comic'
if ($LASTEXITCODE -ne 0) { throw 'Commit failed' }
Write-Output 'Comic commit prepared. Push this branch, create a PR, verify its checks, and merge before validating production.'
# The scheduler completes the PR and deployment verification; this script never pushes main.
# git -C $repo push origin main
