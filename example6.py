@http.route('/website/attribute/config', type='json', auth='public', website=True)
def website_attribute_config(self):
    """
    Provide website attribute configuration for frontend usage.

    This method returns:
    - List of attribute names that should always remain open
    - Website configuration flags controlling behavior and access

    :return: Dictionary containing attribute configuration and flags
    """
    website = request.website.sudo()

    return {
        'always_open_attributes': website.is_always_open_attribute_ids.with_context(
            lang='en_US'
        ).mapped('name'),
        'is_app_tegel_be': website.is_app_tegel_be,
        'restrict_redirect': website.restrict_redirect
    }