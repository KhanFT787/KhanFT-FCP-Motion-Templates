import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium') if False else await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1012, 'height': 800}, device_scale_factor=2)
        for src, out in (('p1.html', 'Paper Page 1.png'), ('p2.html', 'Paper Page 2.png')):
            await pg.goto('file:///home/claude/kft/src/paper/' + src); await pg.wait_for_timeout(500)
            await pg.screenshot(path=out, full_page=True)
        await b.close()
asyncio.run(main())
