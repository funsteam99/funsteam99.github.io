"""Verify comic YouTube video data and rendered embeds."""
from pathlib import Path
import json
import re


YT_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def parse_comic_videos_yml(path: Path) -> dict[str, dict[str, str]]:
    """Parse the simple two-level _data/comic_videos.yml without external deps."""
    entries: dict[str, dict[str, str]] = {}
    current_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1].strip()
            assert current_key not in entries, f"Duplicate comic_videos key: {current_key}"
            entries[current_key] = {}
        elif line.startswith("  ") and current_key is not None and ":" in line:
            k, v = line.strip().split(":", 1)
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
                v = v[1:-1]
            entries[current_key][k.strip()] = v
        else:
            raise AssertionError(f"Unexpected line in {path}: {raw_line}")
    return entries


def main() -> None:
    videos = parse_comic_videos_yml(Path("_data/comic_videos.yml"))
    panels = json.loads(Path("_data/comic_panels.json").read_text(encoding="utf-8"))
    episodes = json.loads(Path("_data/journey_episodes.json").read_text(encoding="utf-8"))

    assert videos, "_data/comic_videos.yml must not be empty"
    for comic_id, meta in videos.items():
        assert comic_id in panels, f"Unknown comic_id in comic_videos.yml: {comic_id}"
        yt_id = meta.get("youtube_id", "")
        assert YT_ID_RE.match(yt_id), f"Invalid youtube_id for {comic_id}: {yt_id!r}"
        assert meta.get("title"), f"Missing title for {comic_id}"

    root = Path("_site")
    if not root.exists():
        print(f"PASS (data only, _site not built): {len(videos)} comic videos validated")
        return

    # 1. Verify modern-journey page embeds every mapped episode video after its panel reader
    mj_html = (root / "modern-journey/index.html").read_text(encoding="utf-8")
    for ep in episodes:
        cid = ep["id"]
        if cid in videos:
            yt_id = videos[cid]["youtube_id"]
            assert f'data-youtube-id="{yt_id}"' in mj_html, f"Missing embed for {cid} ({yt_id})"
            assert f"https://www.youtube.com/watch?v={yt_id}" in mj_html, f"Missing watch link for {cid}"
            # Verify the embed sits inside the episode's <article> and after </section>
            art_marker = f'id="{ep["anchor"]}"'
            art_start = mj_html.index(art_marker)
            art_end = mj_html.index("</article>", art_start)
            art_block = mj_html[art_start:art_end]
            sec_end = art_block.index("</section>")
            vid_pos = art_block.index(f'data-youtube-id="{yt_id}"')
            assert vid_pos > sec_end, f"Video for {cid} must appear below panel-reader section"

    # 2. Verify published science pages
    science_pages = {
        "science/sound-transmission": "sound",
        "science/why-four-seasons": "seasons",
        "science/battery-lightbulb": "battery",
        "science/how-airplanes-fly": "airplanes",
    }
    state_path = Path("_operations/science-release-state.json")
    if state_path.exists():
        for cid, rel in json.loads(state_path.read_text(encoding="utf-8")).items():
            page = rel["url"].split("https://shezi.org.tw/", 1)[1].rstrip("/")
            science_pages[page] = cid

    checked_science = 0
    for page, cid in science_pages.items():
        if cid not in videos:
            continue
        html = (root / page / "index.html").read_text(encoding="utf-8")
        yt_id = videos[cid]["youtube_id"]
        assert f'data-youtube-id="{yt_id}"' in html, f"Missing embed in {page} ({yt_id})"
        assert f"https://www.youtube.com/watch?v={yt_id}" in html, f"Missing watch link in {page}"
        assert html.index(f'data-youtube-id="{yt_id}"') > html.index("</section>", html.index('class="panel-reader"')), (
            f"Video in {page} must appear below panel-reader section"
        )
        checked_science += 1

    # 3. Verify footer YouTube channel link
    home_html = (root / "index.html").read_text(encoding="utf-8")
    assert "https://www.youtube.com/@steamfun3507" in home_html, "Footer YouTube link missing"

    print(
        f"PASS: {len(videos)} comic videos validated "
        f"(modern-journey + {checked_science} published science pages + footer link)"
    )


if __name__ == "__main__":
    main()
