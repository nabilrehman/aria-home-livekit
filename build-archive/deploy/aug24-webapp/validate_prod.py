"""Playwright validation of the LIVE storefront with a real Firebase login (Sarah)."""
import json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "https://aug24-web-549403515075.us-central1.run.app/"
S = Path(__file__).parent  # expects .fbcfg / .sarahpass beside it (not committed)
KEY = [x for x in (S / ".fbcfg").read_text().split(",") if x.startswith("FIREBASE_API_KEY=")][0].split("=", 1)[1]
PW = (S / ".sarahpass").read_text().strip()
fails, notes = [], []
def check(ok, label, detail=""):
    (notes if ok else fails).append(f"{'PASS' if ok else 'FAIL'}  {label}" + (f" — {detail}" if detail else ""))

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome"); pg = b.new_page(viewport={"width": 1440, "height": 900})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    bad = []; pg.on("response", lambda r: bad.append((r.status, r.url)) if r.status >= 400 and "favicon" not in r.url else None)

    pg.goto(BASE, wait_until="networkidle"); pg.wait_for_timeout(800)
    check(pg.locator("text=Trending deals").count() > 0, "home renders")
    imgs = pg.locator("#home img, .pimg img").count(); check(imgs >= 5, "home has product images", str(imgs))
    pg.screenshot(path=str(S / "live_home.png"))

    pg.evaluate("location.hash='#products'"); pg.wait_for_timeout(500)
    check(pg.locator("text=Add to cart").count() >= 5, "products grid")
    pg.locator("text=Add to cart >> visible=true").first.click(); pg.wait_for_timeout(200)
    check("1" in (pg.locator("#cart-n").first.inner_text() if pg.locator("#cart-n").count() else "0"), "cart badge increments")

    # real Firebase sign-in via the UI
    pg.evaluate("location.hash='#support'"); pg.wait_for_timeout(500)
    pg.click("#go-signin"); pg.fill("#email", "sarah@example.com"); pg.fill("#pass", PW); pg.click("#signin")
    pg.wait_for_selector("#s-ready", timeout=20000); pg.wait_for_timeout(1500)
    check("Sarah" in pg.locator("#greet, #meta, #s-ready").first.inner_text() + pg.locator("#s-ready").inner_text(), "signed in as Sarah on Support")
    check(pg.locator("#devices img").count() >= 4, "support rail shows device thumbnails", str(pg.locator("#devices img").count()))
    srcs = [i.get_attribute("src") or "" for i in pg.locator("#devices img").all()]
    check(all("/assets/products/" in s for s in srcs), "rail images come from the catalogue URL", (srcs[:1] or [""])[0][:70])
    check("58121" in pg.locator("#orders").inner_text(), "rail latest order is Sarah's 58121")
    pg.screenshot(path=str(S / "live_support.png"), full_page=True)

    pg.evaluate("location.hash='#my-home'"); pg.wait_for_timeout(700)
    check(pg.locator("#home-devices .hdev").count() == 4, "My Home shows Sarah's 4 devices", str(pg.locator("#home-devices .hdev").count()))
    check("Sarah" in pg.locator("#home-title").inner_text(), "My Home titled for Sarah")
    check(pg.locator("#home-attn").inner_text().strip() == "", "no attention card (all Sarah's devices report)")
    pg.screenshot(path=str(S / "live_myhome.png"), full_page=True)

    pg.evaluate("location.hash='#orders'"); pg.wait_for_timeout(700)
    ords = pg.locator("#orders-page .ord"); check(ords.count() == 2, "Orders page: 2 orders", str(ords.count()))
    check("58121" in ords.first.inner_text(), "newest order first")
    ok_imgs = [i.get_attribute("naturalWidth") for i in pg.locator("#orders-page img").all()]
    nat = pg.evaluate("Array.from(document.querySelectorAll('#orders-page img')).map(i=>i.naturalWidth)")
    check(nat and all(n > 0 for n in nat), "order thumbnails actually load", str(nat))
    pg.screenshot(path=str(S / "live_orders.png"), full_page=True)

    # guest token + signed-in token from the live service
    tok = pg.evaluate("""async () => { const r = await fetch('/token/guest',{method:'POST'}); return r.status }""")
    check(tok == 200, "guest token mints")

    pg.set_viewport_size({"width": 390, "height": 844}); pg.evaluate("location.hash='#home'"); pg.wait_for_timeout(500)
    check(not pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"), "no horizontal scroll on mobile")
    pg.screenshot(path=str(S / "live_mobile.png"), full_page=True)

    check(not errs, "no uncaught JS errors", "; ".join(errs[:2]))
    check(not bad, "no failed requests", "; ".join(f"{s} {u[-50:]}" for s, u in bad[:3]))
    b.close()

print("\n".join(notes + fails)); print(f"\n{len(notes)} passed, {len(fails)} failed"); sys.exit(1 if fails else 0)
