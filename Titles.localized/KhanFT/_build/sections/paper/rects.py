import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1012, 'height': 800}, device_scale_factor=2)
        await pg.goto('file:///home/claude/kft/src/paper/p1.html'); await pg.wait_for_timeout(500)
        r = await pg.evaluate("""['h1','h2','h3'].map(id=>{const rs=[...document.getElementById(id).getClientRects()]; return rs.map(r=>[r.left*2,r.top*2,r.width*2,r.height*2])})""")
        print(json.dumps(r))
        await pg.screenshot(path='Paper Page 1.png', full_page=True)
        await b.close()
asyncio.run(main())
