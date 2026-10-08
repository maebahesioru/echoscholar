"""Record the EchoScholar demo (screen capture of the live audio-first app).

Prereq: server on :7862, fresh state (no kb/topics).
Produces: demo/video/*.webm + demo/marks.json (key timestamps for audio assembly).
"""
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent.parent / "demo"
OUT.mkdir(exist_ok=True)
VID = OUT / "video"
VID.mkdir(exist_ok=True)

APP = "http://127.0.0.1:7862"
marks: list[dict] = []
t0 = time.time()


def mark(name: str) -> None:
    marks.append({"name": name, "t": round(time.time() - t0, 2)})
    print(f"MARK {name} @ {marks[-1]['t']}s", flush=True)


def slow(page, ms=600):
    page.wait_for_timeout(ms)


with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        record_video_dir=str(VID),
        record_video_size={"width": 1280, "height": 800},
    )
    page = ctx.new_page()
    page.on("dialog", lambda d: d.accept())

    page.goto(APP, timeout=60000)
    slow(page, 3500)
    mark("start")

    # upload 3 files
    page.set_input_files(
        "#file",
        [
            str(OUT.parent / "data/sample_course/ml_notes.md"),
            str(OUT.parent / "data/sample_course/lecture_slides.pptx"),
            str(OUT.parent / "data/sample_course/lecture_transcript.vtt"),
        ],
    )
    slow(page, 8000)
    mark("uploaded")

    # analyze
    page.click("#btnAnalyze")
    slow(page, 100000)
    mark("analyzed")
    page.evaluate("window.scrollTo(0, 200)")
    slow(page, 4000)

    # tutor: grounded Q (audio answer!)
    page.click("nav button[data-t='tutor']")
    slow(page, 2000)
    page.fill("#q", "Why is the learning rate important in gradient descent?")
    slow(page, 1500)
    page.click("#btnAsk")
    slow(page, 24000)
    mark("answer_played")
    try:
        page.locator("#chat .cite a").first.click(timeout=5000)
        slow(page, 4500)
    except Exception:
        pass

    # off-material refusal
    page.fill("#q", "What is the capital of France?")
    slow(page, 1200)
    page.click("#btnAsk")
    slow(page, 18000)
    mark("refused")

    # quiz + listen
    page.click("nav button[data-t='quiz']")
    slow(page, 2000)
    try:
        page.locator("#qTopics .chip").first.click(timeout=5000)
    except Exception:
        pass
    slow(page, 1200)
    page.click("#btnQuiz")
    slow(page, 75000)
    mark("quiz_ready")
    page.evaluate("window.scrollTo(0, 320)")
    slow(page, 2500)
    try:
        page.locator(".btnListen").first.click(timeout=6000)
        mark("question_audio")
        slow(page, 12000)
    except Exception:
        pass
    try:
        card = page.locator(".q").first
        card.locator(".opt").first.click(timeout=5000)
        slow(page, 1500)
        card.locator(".btnSubmit").click(timeout=5000)
        mark("feedback_audio")
        slow(page, 14000)
    except Exception:
        pass
    page.evaluate("window.scrollTo(0, 600)")
    slow(page, 3000)

    # dashboard + audio brief
    page.click("nav button[data-t='dash']")
    slow(page, 4000)
    page.click("#btnBrief")
    mark("brief_audio")
    slow(page, 22000)
    page.click("#btnPlan")
    slow(page, 5000)
    page.evaluate("window.scrollTo(0, 0)")
    slow(page, 3500)
    mark("end")

    video = page.video
    ctx.close()
    path = video.path()
    print("VIDEO:", path)
    (OUT / "marks.json").write_text(json.dumps(marks, indent=1))
    print("marks saved")
