class PortalLayoutController(http.Controller):

    @http.route(['/my/orders/update_layout'], type='json', auth="public", website=True)
    def update_order_layout(self, order_id, layout_id, **post):
        """
        Update layout for a sale order from the portal.

        This method:
        - Validates the order existence
        - Ensures only professional partners can update layout
        - Updates the layout_id on the sale order

        :param order_id: ID of the sale order
        :param layout_id: ID of the layout to apply
        :param post: Additional parameters
        :return: Success or error response
        """
        order_sudo = request.env['sale.order'].sudo().browse(int(order_id))
        if not order_sudo.exists() or not order_sudo.partner_id.is_professional:
            return {'success': False, 'error': 'Order not found or access denied'}
        
        # Update layout_id
        order_sudo.write({'layout_id': int(layout_id)})
        
        return {'success': True}