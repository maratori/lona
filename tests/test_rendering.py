async def test_rendering(lona_project_context):
    """
    This test tests all client side rendering features, using the rendering
    test view in the test project.

    The test has two phases: DOM tests, where DOM elements get manipulated, and
    a CSS phase, where the browsers style API gets used.

    The DOM phase is pretty simple and straightforward: The view creates and
    manipulates a simple DOM tree and sends it to the client to render it. The
    rendered HTML has to be equal to the servers representation of the DOM.

    In the CSS phase we can't just check the servers style attributes against
    the clients style attributes, because Lona does not define defaults for
    properties that are not set by the user. In the browser all CSS properties
    always have a value.
    """

    import os

    from playwright.async_api import async_playwright

    from lona.html import HTML

    TEST_PROJECT_PATH = os.path.join(__file__, '../../test_project')

    context = await lona_project_context(
        project_root=TEST_PROJECT_PATH,
        settings=['settings.py'],
    )

    async def next_step(page, number):
        await page.locator('#lona #next-step').click()
        await page.wait_for_selector(f'#lona #step-label>#current:has-text("{number}")')

    async def get_computed_style(page):
        return await page.eval_on_selector(
            '#rendering-root > div',
            'e => getComputedStyle(e)',
        )

    def get_style():
        return context.server.state['rendering-root'][0].style

    async def check_default_styles(page):
        """
        All CSS properties have a specified default value.
        Because we use window.getComputedStyle() to determine CSS values,
        we are required to check our estimated defaults are correct.
        """

        computed_style = await get_computed_style(page)

        assert computed_style['display'] == 'block'
        assert computed_style['position'] == 'static'
        assert computed_style['zIndex'] == 'auto'

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # start rendering test view
        await page.goto(context.make_url('/frontend/rendering/'))
        await page.wait_for_selector('#lona h2:has-text("Rendering Test")')

        rendering_root_element = page.locator('#lona #rendering-root')

        # DOM tests ###########################################################
        for step in range(1, 22):
            await next_step(page, step)

            # get rendered html
            html_string = await rendering_root_element.inner_html()

            # parse and compare html
            html = HTML(f'<div id="rendering-root">{html_string}</div>')[0]

            assert html == context.server.state['rendering-root']

        # CSS tests ###########################################################
        await check_default_styles(page)

        # 22 Set Style
        await next_step(page, 22)

        computed_style = await get_computed_style(page)

        assert computed_style['display'] == 'none'
        assert computed_style['position'] == 'absolute'
        assert computed_style['zIndex'] == 'auto'

        # 23 Add Style
        await next_step(page, 23)

        computed_style = await get_computed_style(page)
        style = get_style()

        assert computed_style['display'] == style['display']
        assert computed_style['position'] == style['position']
        assert computed_style['zIndex'] == style['z-index']

        # 24 Remove Style
        await next_step(page, 24)

        computed_style = await get_computed_style(page)
        style = get_style()

        assert 'display' not in style

        assert computed_style['display'] == 'block'
        assert computed_style['position'] == style['position']
        assert computed_style['zIndex'] == style['z-index']

        # 25 Reset Style
        await next_step(page, 25)

        computed_style = await get_computed_style(page)
        style = get_style()

        assert 'display' not in style
        assert 'z-index' not in style

        assert computed_style['display'] == 'block'
        assert computed_style['position'] == style['position']
        assert computed_style['zIndex'] == 'auto'

        # 26 Clear Style
        await next_step(page, 26)
        await check_default_styles(page)
