 def store_all_attributes_in_session(self, all_products_attrs, product):
        """
        Store all product attributes in session only for
        the scanned product.
        """
        scanned_product_id = request.session.get('scanned_product_id')

        _logger.info("\n\n\n\n")

        _logger.info(
            "[ATTR-SESSION]\n"
            "Called for product tmpl ID=%s\n"
            "Scanned product tmpl ID=%s",
            product.product_tmpl_id.id if product else None,
            scanned_product_id,
        )

        if not scanned_product_id:
            _logger.warning(
                "[ATTR-SESSION]\n"
                "No scanned_product_id found in session.\n"
                "Skipping attribute store."
            )
            return

        if product.product_tmpl_id.id != scanned_product_id:
            _logger.info(
                "[ATTR-SESSION]\n"
                "Product mismatch detected.\n"
                "Current tmpl ID=%s\n"
                "Scanned tmpl ID=%s\n"
                "Skipping attribute store.",
                product.product_tmpl_id.id,
                scanned_product_id,
            )
            return

        request.session['all_attributes'] = all_products_attrs

        _logger.info(
            "[ATTR-SESSION]\n"
            "Attributes stored successfully.\n"
            "Scanned product tmpl ID=%s\n"
            "Total products in attribute map=%s",
            scanned_product_id,
            len(all_products_attrs or {}),
        )
        _logger.info("\n\n\n\n")