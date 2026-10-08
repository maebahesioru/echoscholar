"""YouTube upload v2 — verified, real-mouse, step-by-step.

Usage: python ytup2.py <video.mp4> "<title>"
"""
import sys
import time

from playwright.sync_api import sync_playwright

VIDEO = sys.argv[1]
TITLE = sys.argv[2] if len(sys.argv) > 2 else "Study Companion — demo"
DESCRIPTION = """Study Companion — a source-grounded, adaptive AI tutor.
Multimodal AI Hackathon 2026, Track D: Personalized Tutoring & Adaptive Learning.

Turns your own course material (PDF, slides, notes, lecture transcripts) into a
source-cited knowledge base, then runs grounded tutoring with explicit refusals,
verified adaptive quizzes, and a Bayesian Knowledge Tracing learner model.

Code: https://github.com/maebahesioru/multimodal-study-companion"""


def log(*a):
    print(*a, flush=True)


def click_text(pg, text, tag_filter="button, ytcp-button, tp-yt-paper-radio-button, div[role=button]"):
    """Real-mouse click on the first visible element whose innerText == text."""
    pos = pg.evaluate(
        """([text, sel]) => {
            for (const e of document.querySelectorAll(sel)) {
                const t = (e.innerText || '').trim();
                if (t === text) {
                    e.scrollIntoView({ block: 'center' });
                    const rc = e.getBoundingClientRect();
                    if (rc.width > 0 && rc.height > 0)
                        return { x: Math.round(rc.x + rc.width / 2), y: Math.round(rc.y + rc.height / 2) };
                }
            }
            return null;
        }""",
        [text, tag_filter],
    )
    if not pos:
        log(f'  !! "{text}" not found')
        return False
    pg.mouse.click(pos['x'], pos['y'])
    log(f'  clicked "{text}" @{pos["x"]},{pos["y"]}')
    return True


with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    ctx = browser.contexts[0]
    pg = ctx.new_page()
    pg.on('dialog', lambda d: d.accept())
    pg.bring_to_front()

    pg.goto('https://studio.youtube.com/channel/UCIBl4qUGee47H4wx96rswNw', timeout=90000)
    pg.wait_for_timeout(12000)
    log('page:', pg.url[:100])

    # open the upload dialog: 作成 -> アップロード
    pg.evaluate("""() => {
        const b = [...document.querySelectorAll('a, button, ytcp-button')]
            .find(x => /作成|Create/i.test(x.innerText || x.getAttribute('aria-label') || ''));
        if (b) b.click();
    }""")
    pg.wait_for_timeout(4000)
    pg.evaluate("""() => {
        const items = [...document.querySelectorAll('ytcp-button, tp-yt-paper-item, a, li')]
            .filter(x => /アップロード|Upload/i.test(x.innerText || ''));
        if (items.length) items[0].click();
    }""")
    pg.wait_for_timeout(8000)

    # 1. file
    fi = None
    for _ in range(25):
        fi = pg.query_selector("input[type=file]")
        if fi:
            break
        pg.wait_for_timeout(1500)
    if not fi:
        log('!! no file input found')
        sys.exit(1)
    fi.set_input_files(VIDEO)
    log('file set')
    pg.wait_for_timeout(25000)  # upload + processing + form appears

    # 2. title + description via the details textboxes
    pg.evaluate(
        """([title, desc]) => {
            const boxes = [...document.querySelectorAll('#textbox[contenteditable="true"]')];
            if (boxes[0]) {
                boxes[0].focus();
                document.execCommand('selectAll');
                document.execCommand('insertText', false, title);
            }
            if (boxes[1]) {
                boxes[1].focus();
                document.execCommand('selectAll');
                document.execCommand('insertText', false, desc);
            }
        }""",
        [TITLE, DESCRIPTION],
    )
    log('title+desc set')
    pg.wait_for_timeout(3000)

    # 3. wizard: next x3
    for i in range(3):
        if not click_text(pg, '次へ'):
            # try the aria-label button
            pos = pg.evaluate(
                """() => {
                    const b = document.querySelector('ytcp-button#next-button button, #next-button');
                    if (b) { const rc = b.getBoundingClientRect(); return { x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2) }; }
                    return null;
                }"""
            )
            if pos:
                pg.mouse.click(pos['x'], pos['y'])
                log(f'  clicked next(aria) @{pos["x"]},{pos["y"]}')
        pg.wait_for_timeout(6000)

    # 4. visibility = unlisted — find radio, click, VERIFY aria-checked
    ok = pg.evaluate(
        """() => {
            const radios = [...document.querySelectorAll('tp-yt-paper-radio-button, ytcp-radio-button')];
            for (const r of radios) {
                const t = (r.innerText || '');
                if (/限定公開/.test(t)) {
                    r.scrollIntoView({ block: 'center' });
                    const rc = r.getBoundingClientRect();
                    return { x: Math.round(rc.x + rc.width/2), y: Math.round(rc.y + rc.height/2), checked: r.getAttribute('aria-checked') };
                }
            }
            return null;
        }"""
    )
    log('unlisted radio:', ok)
    if ok:
        pg.mouse.click(ok['x'], ok['y'])
        pg.wait_for_timeout(2500)
        state = pg.evaluate(
            """() => {
                const radios = [...document.querySelectorAll('tp-yt-paper-radio-button, ytcp-radio-button')];
                for (const r of radios) {
                    if (/限定公開/.test(r.innerText || '')) return 'aria-checked=' + r.getAttribute('aria-checked');
                }
                return 'nf';
            }"""
        )
        log('  after click:', state)

    # 5. final button: prefer 保存/公開
    for label in ['保存', '公開', 'Save', 'Publish']:
        if click_text(pg, label):
            break
    pg.wait_for_timeout(20000)

    # 6. verify via content list
    pg.goto('https://studio.youtube.com/channel/UCIBl4qUGee47H4wx96rswNw/videos/upload', timeout=90000)
    pg.wait_for_timeout(12000)
    rows = pg.evaluate(
        """() => {
            const out = [];
            document.querySelectorAll('ytcp-video-row').forEach(r => {
                const t = (r.innerText || '').split('\\n').slice(0, 5).join(' / ');
                out.push(t.slice(0, 110));
            });
            return out.slice(0, 4).join('\\n');
        }"""
    )
    log('ROWS:')
    log(rows)
