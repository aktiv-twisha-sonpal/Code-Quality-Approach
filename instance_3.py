 def _get_website_pricelists_domain(self, website):
        """
        Same logic as Odoo base, but using ONLY website_ids (M2M).
        website_id (M2O) is intentionally ignored.
        """
        return [
            ('active', '=', True),
            ('company_id', 'in', [False, website.company_id.id]),

            # website-specific OR global
            '|',
                ('website_ids', 'in', [website.id]),
                ('website_ids', '=', False),

            # selectable OR coupon (unchanged)
            '|',
                ('selectable', '=', True),
                ('code', '!=', False),
        ]