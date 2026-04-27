@http.route('/shop/set_qr_user_type', type='json', auth='public', website=True)
def set_qr_user_type(self, user_type):
    """
    Set QR user type in session.

    Stores the selected user type (customer or professional)
    in the session for later use in pricing and access logic.

    :param user_type: Selected user type
    :return: Success response
    """
    if user_type in ('customer', 'professional'):
        request.session['qr_user_type'] = user_type
    return {"success": True}


@http.route('/website/reset_pricelist_session', type='json', auth='public', website=True)
def reset_pricelist_session(self):
    """
    Reset QR user type from session.

    Clears the stored user type used for pricing logic.

    :return: Success response
    """
    request.session.pop('qr_user_type', None)
    return {"success": True}


@http.route(
    '/website/current_pricelists',
    type='json',
    auth='public',
    website=True
)
def get_current_pricelists(self):
    """
    Fetch current pricelists for the user.

    This method:
    - Retrieves pricelists based on QR user type
    - Returns current selected pricelist from session
    - Formats display name using partner-level logic

    :return: Dictionary containing current pricelist and available pricelists
    """
    website = request.website.sudo()
    partner = request.env.user.partner_id.sudo()

    pricelists = website.get_pricelist_for_user(
        request.session.get('qr_user_type')
    ).sudo()

    current_pricelist_id = request.session.get('website_sale_current_pl')

    return {
        'current_pricelist_id': current_pricelist_id,
        'pricelists': [
            {
                'id': pricelist.id,
                'name': pricelist.name,
                'display_name': partner._get_pricelist_display_name(
                    pricelist=pricelist,
                    match_contact_pricelist_only=True,
                ),
                'currency_id': pricelist.currency_id.id,
                'currency_name': pricelist.currency_id.name,
            }
            for pricelist in pricelists
        ]
    }