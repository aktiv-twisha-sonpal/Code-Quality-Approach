 # ==================================================
    # PRODUCT PAGE (CLEAN URL + QR LOGIC)
    # ==================================================
    @http.route(
        [
            '/shop/product/<string:slug>/<string:default_code>',
            '/shop/art/<string:default_code>',
            '/art/<string:default_code>',
        ],
        type='http',
        auth='public',
        website=True
    )
    def product_custom_slug(self, default_code, slug=None, **kwargs):
        

        # --------------------------------------------------
        # RESET SESSION IF WEBSITE CHANGED
        # --------------------------------------------------
        self._reset_qr_session_if_website_changed()


        env = request.env(context=dict(request.env.context, lang='en_US'))
        if not request.session.get('qr_accessed'):
            request.session['qr_accessed'] = False
        # --------------------------------------------------
        # GET PRODUCT
        # --------------------------------------------------
        product = env['product.template'].sudo().search(
            [('default_code', '=', default_code)],
            limit=1
        )
        if not product:
            raise NotFound()

        clean_url = f"/art/{default_code}"
        qr_token = request.params.get('qr_token')
        # --------------------------------------------------
        # QR ENTRY (ONLY FIRST HIT)
        # --------------------------------------------------
        if qr_token:
           
            request.session.update({
                'allowed_qr_path': clean_url,
                'qr_accessed': True,
                'scanned_product_id': product.id,
                'joint_suggestion_ids': product.joint_suggestion_ids.ids or [],
                'silicone_sealant_id': product.silicone_sealant_id.id or None
            })

        # --------------------------------------------------
        # FORCE CLEAN URL (REMOVE ?qr_token)
        # --------------------------------------------------
        redirect = self._redirect_to_clean_app_url(clean_url, product)
        if redirect:
            return redirect

        # --------------------------------------------------
        # VALIDATE ACCESS (QR RESTRICTION)
        # --------------------------------------------------
        allowed_templates = env['product.template'].sudo().browse([])

        # 1) scanned product
        scanned_product_id = request.session.get('scanned_product_id')
        if scanned_product_id:
            allowed_templates |= env['product.template'].sudo().browse(scanned_product_id)

        # 2) joint suggestions
        joint_ids = request.session.get('joint_suggestion_ids', [])
        if joint_ids:
            allowed_templates |= env['product.template'].sudo().browse(joint_ids).filtered(
                lambda p: p.active and p.sale_ok and p.website_published
            )

        # 3) attribute-related products
        all_attrs = request.session.get('all_attributes')
        related_products = []
        if all_attrs:
            for key,value in all_attrs.items():   
                related_products.append(value.get('id'))
        _logger.info("========== Related products session data: %s ==========", related_products)
        if related_products:
            allowed_templates |= env['product.template'].sudo().browse(related_products)

        # 4) silicone sealant
        silicone_sealant_id = request.session.get('silicone_sealant_id')
        if silicone_sealant_id:
            allowed_templates |= env['product.template'].sudo().browse(silicone_sealant_id)

        _logger.info(
            "========== Allowed templates session data: %s ==========",
            allowed_templates.ids
        )

        if request.website.restrict_redirect and not request.env.user._is_admin():
            _logger.info(
                "[QR-ACCESS]\n"
                "Restrict redirect is enabled.\n"
                "Validating product access.\n"
                "Requested product ID: %s\n"
                "Allowed template IDs: %s\n"
                "QR accessed: %s",
                product.id,
                allowed_templates.ids,
                request.session.get('qr_accessed'),
            )
            if request.session.get('qr_accessed') == False:
               
                raise NotFound()

            if (
                allowed_templates
                and product.id not in allowed_templates.ids
            ):
                _logger.warning(
                    "[QR-ACCESS]\n"
                    "Access denied.\n"
                    "Product ID %s is not in allowed templates.\n"
                    "Raising NotFound.",
                    product.id,
                )
                raise NotFound()



        # --------------------------------------------------
        # POPUP LOGIC
        # --------------------------------------------------
        show_popup = (
            request.session.get('qr_accessed')
            and not request.session.get('qr_user_type')
            and request.website.is_app_tegel_be
        )

        kwargs.pop('search', None)
        kwargs.pop('category', None)

        # --------------------------------------------------
        # RENDER PRODUCT PAGE
        # --------------------------------------------------
        values = WebsiteSale()._prepare_product_values(product, '', '', **kwargs)
        values.update({
            'show_user_type_popup': show_popup,
        })

        return request.render("website_sale.product", values)

    # ==================================================
    # CLEAN URL REDIRECT HELPER
    # ==================================================
    def _redirect_to_clean_app_url(self, clean_url, product):
        """
        Redirect ONLY scanned product
        Remove ALL query params (?qr_token, etc.)
        """

        env = request.env(context=dict(request.env.context, lang='en_US'))
        Website = env['website'].sudo()

        app_website = Website.search(
            [('is_app_tegel_be', '=', True)],
            limit=1
        )
        if not app_website:
            return False

        scanned_product_id = request.session.get('scanned_product_id')

        #  redirect only scanned product
        if scanned_product_id != product.id:
            return False

        current_path = request.httprequest.path
        has_query = bool(request.httprequest.query_string)

        # Redirect if URL is not clean
        if current_path != clean_url or has_query:
            app_base_url = app_website.get_base_url()
            return request.redirect(f"{app_base_url}{clean_url}")

        return False