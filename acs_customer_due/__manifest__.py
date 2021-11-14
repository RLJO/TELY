#╔══════════════════════════════════════════════════════════════════╗
#║                                                                  ║
#║                ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                 ║
#║                ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                 ║
#║                ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                 ║
#║                ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                 ║
#║                ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                 ║
#║                ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                 ║
#║                          ╔═╝║     ╔═╝║                           ║
#║                          ╚══╝     ╚══╝                           ║
#║ SOFTWARE DEVELOPED AND SUPPORTED BY ALMIGHTY CONSULTING SERVICES ║
#║                   COPYRIGHT (C) 2016 - TODAY                     ║
#║                   http://www.almightycs.com                      ║
#║                                                                  ║
#╚══════════════════════════════════════════════════════════════════╝
{
    'name': "Customer Due Payment",
    'version': '12.0.2.4',
    'summary': """Customer Due Payment for Customer and Supplier""",
    'description': """
        This module adds Customer Due payment report for Partners, almihgtycs acs hms patient due payments customer due payment report
        partner due report vendor due report partner statement vendor statement customer statement due payments total

        In diesem Modul wird der Customer Due-Zahlungsbericht für Partner hinzugefügt
         Partnerfälligkeitsbericht Lieferantenfälligkeitsbericht Partnererklärung Lieferantenerklärung Kundenaussage fällige Zahlungen insgesamt
        
        Ce module ajoute le rapport de paiement dû par le client pour les partenaires, almihgtycs acs hms le paiement dû par le patient le rapport de paiement dû par le client.
         rapport du partenaire dû rapport du fournisseur rapport du partenaire déclaration du fournisseur relevé du client relevé des paiements échus total

        Este módulo agrega el informe de pagos debidos de clientes para socios, almihgtycs acs hms pacientes pagos debidos informe de pagos debidos de clientes
         informe de vencimiento del socio informe de vencimiento del proveedor informe de asociado declaración de proveedor resumen de pagos debidos del cliente total

    """,
    'author': "Almighty Consulting Services",
    'company': 'Almighty Consulting Services',
    'website': 'https://www.almightycs.com',
    'license': 'OPL-1',
    'support': 'info@almightycs.com',
    'category': 'Accounting',
    'depends': ['base', 'base_setup', 'account','mail'],
    'data': [
        'report/customer_due_report.xml',
        'data/mail_template_data.xml',
        'secutiry/group_journal.xml',
        #'security/group_journal.xml',
        'wizard/customer_report_wizard.xml',
    ],
    'images': [
        'static/description/acs_customer_due_almightycs_cover.jpg',
    ],
    'installable': True,
    'application': False,
    'sequence': 1,
    'price': 25,
    'currency': 'EUR',
}