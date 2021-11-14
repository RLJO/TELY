odoo.define('bi_car_repair_management.car_request', function (require) {
'use strict';
	var ajax = require('web.ajax');
	var core = require('web.core');
	var Widget = require('web.Widget');
	var qweb = core.qweb;

	var portalchatter = require('portal.chatter');

	portalchatter.PortalChatter.include({
		_loadTemplates: function(){
        	return $.when(this._super(), ajax.loadXML('/bi_car_repair_management/static/src/xml/chatter.xml', qweb));
    	},
	})

	$(document).ready(function() {

     	if($('#product_id') != null){
			
			$('#product_id').on('change',function(event) {
				event.stopPropagation();
	        	event.preventDefault();
				var car_id = this.value;

				ajax.jsonRpc('/action/send', 'call', {'car_id':car_id}).then(function(request_data)
					{
						var data = JSON.parse(request_data);
						$('#model').val(data.model_id);
						$('#brand').val(data.brand_id);
						$('#year').val(data.year);						
					});
			});
		}
    });
});