# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class stock_packaging_add_type(orm.Model):
    _name = 'stock.packaging.add.type'
    
    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.char('Name', size=64),
    }

class stock_packaging_add(orm.TransientModel):

    _name = "stock.packaging.add"
    _description = "Add objects to a pack"
    
    _columns = {
        'product_ids': fields.one2many('stock.packaging.add.line', 'parent_id', 'Lines'),
        'type_id': fields.many2one('stock.packaging.add.type', 'Type', required=True),
        'type': fields.char('Type', size=64),
        'pack_id': fields.many2one('stock.tracking', 'Pack to move', required=True),
    }

    def _get_type_id(self, cr, uid, context):
        if context==None:
            context={}
        if context.get('type_selection'):
            type = context.get('type_selection')
        else:
            type = 'product'
        type_obj = self.pool.get('stock.packaging.add.type')
        default_type = type_obj.search(cr, uid, [('code', '=', type)], limit=1, context=context)
        if not default_type:
            default_type = type_obj.search(cr, uid, [], limit=1, context=context)
        return default_type and default_type[0] or False

    def _get_type(self, cr, uid, context):
        if context==None:
            context={}
        if context.get('type_selection'):
            type = context.get('type_selection')
        else:
            type = 'product'
        res_type = ''
        type_obj = self.pool.get('stock.packaging.add.type')
        default_type = type_obj.search(cr, uid, [('code', '=', type)], limit=1, context=context)
        if not default_type:
            default_type = type_obj.search(cr, uid, [], limit=1, context=context)
        if default_type and default_type[0]:
            read_type = type_obj.read(cr, uid, default_type[0], ['code'], context=context)
            if read_type['code']:
                res_type = read_type['code']
        return res_type or ''

    _defaults = {
        'pack_id': lambda self, cr, uid, context: context.get('active_id') or False,
        'type_id': lambda self, cr, uid, context: self._get_type_id(cr, uid, context),
        'type': lambda self, cr, uid, context: self._get_type(cr, uid, context),
    }
    
    def onchange_type_id(self, cr, uid, ids, type_id):
        res = {'value': {'type': ''}}
        if type_id:
            type_obj = self.pool.get('stock.packaging.add.type')
            type = type_obj.read(cr, uid, type_id, ['code'])
            if type['code']:
                res = {'value': {'type': type['code']}}
        return res
    
    
    def add_object(self, cr, uid, ids, context=None):
        # Initialization #
        if context == None:
            context = {}
        tracking_obj = self.pool.get('stock.tracking')
        # Process #
        for current in self.browse(cr, uid, ids, context=context):
            
            pack_id = current.pack_id.id
            type = current.type_id.code
            # Creation of an empty list for the product, and empty dictionary for the quantity"
            quantities = {}
            product_ids = []
            if type == 'product':
                for line_data in current.product_ids:
                    # For each product added, we appends at the product_ids list the quantity added #
                    product_ids.append(line_data.product_id.id)
                    quantities[line_data.product_id.id]=line_data.quantity
                # call functions add product with argument pack_id , products_ids and quantities #
                tracking_obj.add_products(cr, uid, pack_id, product_ids, quantities, context=context)
        return {'type': 'ir.actions.act_window_close'}
       
class stock_packaging_add_line(orm.TransientModel):

    _name = "stock.packaging.add.line"
    _description = "Add object to a pack"
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', domain="[('type', '!=', 'service'),('track_outgoing', '=', False)]"),
        'parent_id': fields.many2one('stock.packaging.add', 'Parent'),
        'location_id': fields.many2one('stock.location', 'Location'),
        'quantity': fields.float('Quantity', required=True),
    }
    
    _defaults = {
        'quantity': 1.0,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: