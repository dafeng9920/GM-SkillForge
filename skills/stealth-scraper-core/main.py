import os
import time
import random
import asyncio
import subprocess
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright, TimeoutError
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Stealth Scraper Core v1")

# Ensure logs directory exists
LOG_DIR = "/app/logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def ensure_xvfb():
    """
    Improved Xvfb management: Clean lock correctly and ensure it's up.
    """
    try:
        subprocess.run(["xdpyinfo", "-display", ":99"], check=True, capture_output=True)
    except:
        print("Xvfb on :99 not found. Cleaning locks and starting...")
        # Deep clean locks
        for f in ["/tmp/.X99-lock", "/tmp/.X11-unix/X99"]:
            try: os.remove(f)
            except: pass
        subprocess.Popen(["Xvfb", ":99", "-screen", "0", "1280x720x24", "-ac", "+extension", "GLX", "+render", "-noreset"])
        time.sleep(3)

@app.get("/health")
async def health_check():
    """Lightweight health check for automation."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

async def apply_stealth_manually(page):
    """
    World-class "Human" Stealth Implementation (Manual Script Injection).
    Returns a human_jitter function to be used during scraping.
    """
    await page.add_init_script("delete Object.getPrototypeOf(navigator).webdriver")
    
    # 1. Standard Jitter Logic
    async def jitter_func():
        try:
            for _ in range(random.randint(1, 3)):
                x, y = random.randint(100, 600), random.randint(100, 600)
                await page.mouse.move(x, y, steps=10)
                await asyncio.sleep(random.uniform(0.1, 0.4))
        except: pass

    # 2. Page Scripts
    await page.add_init_script("""
        window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'NVIDIA GeForce RTX 5070 Ti';
            return originalGetParameter.apply(this, arguments);
        };
    """)
    return jitter_func

@app.get("/v1/check_fingerprint")
async def check_fingerprint():
    """
    Diagnostic endpoint to verify GPU Renderer and Stealth success.
    """
    ensure_xvfb()
    os.environ["DISPLAY"] = ":99"
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False, args=["--no-sandbox", "--display=:99"])
            context = await browser.new_context(viewport={'width': 1280, 'height': 720})
            page = await context.new_page()
            # Capture return even if unused
            _ = await apply_stealth_manually(page)
            await page.goto("https://browserleaks.com/webgl", wait_until="networkidle", timeout=60000)
            renderer = await page.get_attribute("#unmasked-renderer", "innerText") or "Unknown"
            vendor = await page.get_attribute("#unmasked-vendor", "innerText") or "Unknown"
            screenshot_path = os.path.join(LOG_DIR, f"fingerprint_{int(time.time())}.png")
            await page.screenshot(path=screenshot_path)
            await browser.close()
            return {"status": "success", "renderer": renderer, "vendor": vendor, "screenshot": screenshot_path}
        except Exception as e:
            if 'browser' in locals(): await browser.close()
            return {"status": "error", "message": str(e)}

@app.get("/v1/scrape/x")
async def scrape_x(target_user: str, depth: int = 5, proxy: str = None):
    """
    Enhanced Stealth Scraper for X (KOL Content Engine).
    """
    ensure_xvfb()
    os.environ["DISPLAY"] = ":99"
    async with async_playwright() as p:
        launch_args = ["--no-sandbox", "--disable-setuid-sandbox", "--display=:99"]
        if proxy: launch_args.append(f"--proxy-server={proxy}")

        try:
            browser = await p.chromium.launch(headless=False, args=launch_args)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            human_jitter = await apply_stealth_manually(page)

            # 1. Improved Navigation with Loading Detection
            try:
                await page.goto(f"https://x.com/{target_user}", wait_until="networkidle", timeout=60000)
                spinner_selector = "[role='progressbar']"
                try: await page.wait_for_selector(spinner_selector, state="hidden", timeout=20000)
                except: pass
            except Exception as e:
                print(f"Navigation warning: {str(e)}")

            try:
                # Combined selector for robustness
                tweet_selector = "[data-testid='tweet'], article, [role='article']"
                
                # RECOVERY LOGIC: Detect "Something went wrong"
                for _ in range(2): # Try retry/refresh twice
                    if await page.query_selector("text=Something went wrong"):
                        print(f"Detected 'Something went wrong' for {target_user}. Attempting recovery...")
                        retry_btn = await page.query_selector("text=Retry")
                        if retry_btn:
                            await retry_btn.click()
                            await asyncio.sleep(5)
                        else:
                            await page.reload(wait_until="networkidle")
                    
                    if await page.query_selector(tweet_selector):
                        break
                
                # INITIAL AGGRESSIVE SCROLL: Force X to wake up
                await page.mouse.wheel(0, 800)
                await asyncio.sleep(3)
                
                await page.wait_for_selector(tweet_selector, timeout=45000)
            except Exception as e:
                # FINAL ATTEMPT: One more scroll
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(5)
                if not await page.query_selector(tweet_selector):
                    screenshot_path = os.path.join(LOG_DIR, f"timeout_{target_user}_{int(time.time())}.png")
                    await page.screenshot(path=screenshot_path)
                    await browser.close()
                    return {"status": "error", "reason": "X_ERROR: 'Something went wrong' persisted after retries.", "evidence": screenshot_path}
                
            all_data = []
            seen_tweet_ids = set()

            # 3. Pre-scroll & Jitter
            await human_jitter() 
            await page.mouse.wheel(0, 500)
            await asyncio.sleep(2)

            # 4. Deep Scrolling & Extraction Loop
            for i in range(depth):
                if i % 2 == 0: await human_jitter()
                
                show_more_buttons = await page.query_selector_all("text=Show more")
                for btn in show_more_buttons:
                    try: await btn.click(); await asyncio.sleep(0.8)
                    except: pass

                tweets = await page.query_selector_all("[data-testid='tweet'], article")
                for tweet in tweets:
                    try:
                        text_element = await tweet.query_selector("[data-testid='tweetText'], .tweet-text")
                        if not text_element: continue
                        
                        text = await text_element.inner_text()
                        tweet_hash = hash(text[:100])

                        if tweet_hash not in seen_tweet_ids:
                            engagement = {"replies": "0", "retweets": "0", "likes": "0"}
                            for m_type in ["reply", "retweet", "like"]:
                                try:
                                    val = await tweet.eval_on_selector(f"[data-testid='{m_type}']", "e => e.innerText")
                                    engagement[m_type] = val if val else "0"
                                except: pass
                            
                            all_data.append({
                                "text": text,
                                "engagement": engagement,
                                "scraped_at": datetime.now().isoformat()
                            })
                            seen_tweet_ids.add(tweet_hash)
                    except: continue

                await page.mouse.wheel(0, random.randint(1000, 1500))
                await asyncio.sleep(random.uniform(2, 4))

            await browser.close()
            return {"status": "success", "user": target_user, "total_captured": len(all_data), "data": all_data}
        except Exception as e:
            if 'browser' in locals(): await browser.close()
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
