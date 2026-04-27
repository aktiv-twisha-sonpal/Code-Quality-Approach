@http.route(
    '/website/snippet/autocomplete',
    type='json',
    auth='public',
    website=True,
    readonly=True
)
def autocomplete(
        self,
        search_type=None,
        term=None,
        order=None,
        limit=5,
        max_nb_chars=999,
        options=None
):
    """
    Override autocomplete to control product price visibility.

    This method:
    - Calls the default autocomplete behavior
    - Applies website-level and product-level price hiding rules
    - Removes price-related fields from results when required
    - Ensures consistent price visibility in search suggestions

    :param search_type: Type of search
    :param term: Search term
    :param order: Sorting order
    :param limit: Maximum number of results
    :param max_nb_chars: Maximum characters in result
    :param options: Additional options
    :return: Modified autocomplete response
    """
    # ------------------------------------------------------------
    # Call original autocomplete (UNCHANGED)
    # ------------------------------------------------------------
    response = super().autocomplete(
        search_type=search_type,
        term=term,
        order=order,
        limit=limit,
        max_nb_chars=max_nb_chars,
        options=options,
    )

    if not response or not response.get('results'):
        return response

    website = request.website.sudo()
    website_hide_price = website.hide_price_in_website

    Product = request.env['product.template'].sudo()

    # ------------------------------------------------------------
    # PROCESS RESULTS
    # ------------------------------------------------------------
    for res in response.get('results', []):

        # Start with website-level rule
        hide_price = website_hide_price

        website_url = res.get('website_url')
        if not website_url:
            continue

        product_default_code = website_url.rstrip('/').split('/')[-1]
        product = Product.search(
            [('default_code', '=', product_default_code)],
            limit=1
        )

        if not product:
            continue

        # --------------------------------------------------------
        # PRODUCT-LEVEL HIDE
        # --------------------------------------------------------
        if product.hide_product_price(product, website):
            hide_price = True

        # --------------------------------------------------------
        # REMOVE PRICE FROM RESULT
        # --------------------------------------------------------
        if hide_price:
            res.pop('detail', None)
            res.pop('detail_extra', None)
            res.pop('detail_strike', None)

    # ------------------------------------------------------------
    # GLOBAL PARTS HIDE
    # ------------------------------------------------------------
    if website_hide_price:
        response.get('parts', {}).pop('detail', None)

    return response