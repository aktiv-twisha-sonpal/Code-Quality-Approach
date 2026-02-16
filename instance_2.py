def _get_current_pricelist(self):
        """
        Return the active website pricelist.
        """
        self.ensure_one()

        partner = self.env.user.partner_id
        is_professional_user = partner.is_professional

        _logger.info("========== Default PRICELIST RESOLUTION START ==========")
        _logger.info("User ID: %s | Partner ID: %s", self.env.user.id, partner.id)
        _logger.info("Is professional user: %s", is_professional_user)
        _logger.info("QR user type (session): %s", request.session.get("qr_user_type"))

        allowed_pricelists = self.get_pricelist_for_user(
            request.session.get("qr_user_type")
        )

        _logger.info(
            "Allowed pricelists from QR logic: %s",
            allowed_pricelists.ids if allowed_pricelists else []
        )

        # Fallback to standard pricelist if no restriction applies
        if not allowed_pricelists:
            allowed_pricelists = self.standard_pricelist_id
            _logger.info(
                "No QR-based pricelist found. Falling back to standard pricelist: %s",
                allowed_pricelists.id if allowed_pricelists else None
            )

        current_pricelist_id = request.session.get("website_sale_current_pl")
        _logger.info("Current session pricelist ID: %s", current_pricelist_id)

        # If only one pricelist is allowed, enforce it directly
        if len(allowed_pricelists) == 1:
            request.session["website_sale_current_pl"] = allowed_pricelists.id
            _logger.info(
                "Only one allowed pricelist. Forcing pricelist ID: %s",
                allowed_pricelists.id
            )
            return allowed_pricelists

        # Reset cached pricelist if it is no longer allowed
        if not current_pricelist_id or current_pricelist_id and current_pricelist_id not in allowed_pricelists.ids:
            _logger.warning(
                "Cached pricelist %s is not allowed anymore. Resetting...",
                current_pricelist_id
            )

            partner_pricelist_id = partner.property_product_pricelist.id
            _logger.info(
                "Partner property pricelist ID: %s",
                partner_pricelist_id
            )

            if (is_professional_user 
                and partner_pricelist_id 
                and partner_pricelist_id in allowed_pricelists.ids 
               ):
                request.session["website_sale_current_pl"] = partner_pricelist_id
                _logger.info(
                    "Professional user. Using partner pricelist ID: %s",
                    partner_pricelist_id
                )
            else:
                if self.standard_pricelist_id:
                    request.session["website_sale_current_pl"] = self.standard_pricelist_id.id
                    _logger.info(
                        "Using standard pricelist ID: %s",
                        self.standard_pricelist_id.id
                    )
                elif allowed_pricelists:
                    request.session["website_sale_current_pl"] = allowed_pricelists[0].id
                    _logger.info(
                        "Using first allowed pricelist ID: %s",
                        allowed_pricelists[0].id
                    )
                else:
                    _logger.info("No valid pricelist found. Falling back to super().")
                    return super(WebsiteInherit, self)._get_current_pricelist()

        _logger.info("Falling back to Odoo default pricelist resolution.")
        _logger.info("========== Default PRICELIST RESOLUTION END ==========")

        return super(WebsiteInherit, self)._get_current_pricelist()
