@http.route('/website/get_pricelists', type='json', auth='public', website=True)
def get_pricelists(self):
    """
    Fetch all available pricelists for the current website.

    This method retrieves all pricelists accessible on the website,
    typically used for frontend rendering and selection.

    :return: List of pricelists
    """
    website = request.website.sudo()
    return website.get_all_pricelists()