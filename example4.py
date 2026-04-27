def _redirect_to_clean_app_url(self, clean_url):
    """
    Redirect to a clean product URL for app-specific website.

    This method ensures the URL:
    - Matches the expected clean path (without query parameters)
    - Uses the correct app website domain if configured

    If the current request URL differs from the clean URL or contains
    query parameters, a redirect is returned. Otherwise, no action is taken.

    :param clean_url: Expected clean URL path
    :return: Redirect response or False
    """

    env = request.env(context=dict(request.env.context, lang='en_US'))
    Website = env['website'].sudo()
    ConfigParameter = request.env["ir.config_parameter"].sudo()
    base_url = ConfigParameter.get_param("web.base.url", "").rstrip("/")

    app_website = Website.search(
        [('is_app_tegel_be', '=', True)],
        limit=1
    )
    if not app_website:
        return False

    current_path = request.httprequest.path
    has_query = bool(request.httprequest.query_string)
    if current_path != clean_url or has_query:
        app_base_url = app_website.domain or base_url
        return request.redirect(f"{app_base_url}{clean_url}")

    return False