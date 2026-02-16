  def get_pricelist_for_user(self, user_type):
        """
        Retrieve applicable pricelists based on the given user type.

        Debug Version:
        This method logs each decision point to clearly indicate
        why a pricelist is included or excluded during evaluation.

        Notes:
        - For customer users, only the standard pricelist is returned.
        - For professional users, the standard pricelist is not included by default.
        - Pricelist inclusion depends on user type, group membership,
        explicit user assignments, and website configuration.
        """
        self.ensure_one()

        Pricelist = self.env["product.pricelist"]
        user = self.env.user

        is_public_user = user._is_public()
        is_professional_user = user.partner_id.is_professional
        partner_pricelist_id = user.partner_id.property_product_pricelist

        _logger.info("\n================ PRICELIST DEBUG START ================")
        _logger.info("User ID: %s", user.id)
        _logger.info("User name: %s", user.name)
        _logger.info("User type: %s", user_type)
        _logger.info("Is public user: %s", is_public_user)
        _logger.info("Is professional group user: %s", is_professional_user)
        _logger.info("Standard pricelist: %s", self.standard_pricelist_id)
        _logger.info("------------------------------------------------------")

        result_pricelists = Pricelist.browse()  # Empty recordset

        # ------------------------------------------------------------
        # Customer user type
        # ------------------------------------------------------------
        if user_type == "customer":
            _logger.info(
                "Customer user type detected. Returning standard pricelist only."
            )
            return self.end_customer_pricelist or result_pricelists
        
        # --------------------------------------------------------
        # Professional user type
        # --------------------------------------------------------
        if user_type == "professional":
            _logger.info("Professional user type branch entered.")

            if self.installer_partner_pricelist:
                _logger.info(
                    "Included: Professional pricelist configuration applied."
                )
                return self.installer_partner_pricelist

        # ------------------------------------------------------------
        # Iterate through configured application pricelists
        # ------------------------------------------------------------
        if self.is_switch_pricelist:
            for app_pricelist in self.app_tegel_be_pricelist_ids:
                pricelist = app_pricelist.pricelist_id

                _logger.info("\nEvaluating App Pricelist ID: %s", app_pricelist.id)
                _logger.info("Pricelist: %s", pricelist)
                _logger.info("Allowed user IDs: %s", app_pricelist.user_ids.ids)

                if not pricelist:
                    _logger.info("Skipped: No pricelist is linked to this configuration.")
                    continue

                # -------------------------------------------------------
                # Default branch (public and standard logged-in users)
                # --------------------------------------------------------
                _logger.info("Default user branch entered.")

                if app_pricelist.user_ids and user not in app_pricelist.user_ids:
                    _logger.info(
                        "Skipped: Current user is not in the allowed user list."
                    )
                    continue

                _logger.info("Included: Pricelist matched default conditions.")
                result_pricelists |= pricelist

        # ------------------------------------------------------------
        # Fallback and partner-specific pricelist handling
        # ------------------------------------------------------------
        if self.standard_pricelist_id and not self.is_app_tegel_be:
            _logger.info(
                "Adding standard pricelist as fallback: %s",
                self.standard_pricelist_id,
            )
            result_pricelists |= self.standard_pricelist_id

        if (
            is_professional_user
            and self.is_switch_pricelist
            and partner_pricelist_id
            and partner_pricelist_id.website_ids
            and self.id in partner_pricelist_id.website_ids.ids
        ):
            _logger.info(
                "Adding partner-specific pricelist: %s",
                user.partner_id,
            )
            result_pricelists |= user.partner_id.property_product_pricelist

        _logger.info("------------------------------------------------------")
        _logger.info(
            "Final resolved pricelist IDs: %s",
            result_pricelists.ids,
        )
        _logger.info("================ PRICELIST DEBUG END ==================\n")

        return result_pricelists