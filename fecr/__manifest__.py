{
    "name": "FECR",
    "version": "12.0.2.9",
    "category": "Accounting",
    "summary": "Factura electrónica para Costa Rica",
    "author": "XALACHI",
    "website": "https://github.com/xalachi/fecr",
    "license": "LGPL-3",
    "price": 500,
    "currency": "USD",
    "depends": [
        "account",
        "base_iban",
        "l10n_cr",
        "sale",
        "uom",
    ],
    "data": [
        # security
        "security/ir.model.access.csv",
        "security/rule.xml",
        "security/group_usd.xml",
        # templates
        # data
        "data/sequence.xml",  # Special case, this calls a function
        "data/account_journal.xml",
        "data/sale_conditions_data.xml",
        "data/account_payment_term.xml",
        "data/account_tax_data.xml",
        "data/aut_ex_data.xml",
        "data/decimal_accuracy.xml",
        # 'data/cabys.csv',  # Loaded in post_init_hook to improve performance on update
        "data/code_type_product_data.xml",
        "data/config_settings.xml",
        "data/currency_data.xml",
        "data/economic_activity_data.xml",
        "data/identification_type_data.xml",
        "data/ir_cron_data.xml",
        "data/mail_template_data.xml",
        "data/payment_methods_data.xml",
        "data/product_category_data.xml",
        "data/reference_code_data.xml",
        "data/reference_document_data.xml",
        "data/res.country.county.csv",
        "data/res.country.district.csv",
        "data/res.country.neighborhood.csv",  # Loaded in post_init_hook to improve performance on update
        "data/res.country.state.csv",
        "data/res.currency.xml",
        "data/uom_category.xml",
        "data/uom_data.xml",
        # reports
        "reports/account_invoice_ticket.xml",
        "reports/account_invoice.xml",
        # views
        "views/menu_views.xml",  # menus
        "views/account_config_settings.xml",
        "views/account_invoice_import_config.xml",
        "views/account_invoice_line.xml",
        "views/account_invoice_refund.xml",
        "views/account_invoice_tax.xml",
        "wizard/account_invoice_import_view.xml",  # deps: views/account_invoice_views.xml
        "views/account_invoice_views.xml",
        "views/account_journal_dashboard.xml",
        "views/account_journal_views.xml",
        "views/account_payment_term.xml",
        "views/account_payment_views.xml",
        "views/account_tax_views.xml",
        "views/account_tax.xml",
        "views/cabys.xml",
        "views/code_type_product_views.xml",
        "views/identification_type_views.xml",
        "views/partner.xml",
        "views/product_template.xml",
        "views/reference_document_views.xml",
        "views/res_company_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_country_country.xml",
        "views/res_country_district.xml",
        "views/res_country_neighborhood.xml",
        "views/res_partner_views.xml",
        "views/resolution_views.xml",
        "views/sale_condition_views.xml",
        "views/sale_order_views.xml",
        "views/uom_views.xml",
        "views/sale_order_view.xml",  # reporte de ventas
        "views/sale_order_report.xml",  # reporte de ventas
        "views/sale_res_config_settings_views.xml",  # reporte de ventas configuracion
        "wizard/account_invoice_import_view2.xml",
    ],
    "external_dependencies": {
        "python": [
            "cryptography",
            "jsonschema",
            "OpenSSL",
            "phonenumbers",
            "PyPDF2",
            "suds",
            "xmlsig",
        ],
    },
    "post_init_hook": "post_init_hook",
    "images": [
        "static/description/images/screenshot.jpg",
        "static/description/images/config.jpg",
    ],
}
