# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestOnchange(common.TransactionCase):
    def test_playing_onchange_on_model(self):
        result = self.env["res.partner"].play_onchanges(
            {
                "company_type": "company",
            },
            ["company_type"],
        )
        self.assertEqual(result["is_company"], True)

    def test_playing_onchange_on_record(self):
        company = self.env.ref("base.main_company")
        result = company.play_onchanges({"email": "contact@akretion.com"}, ["email"])
        self.assertEqual(
            result["rml_footer"],
            "Phone: +1 555 123 8069 | Email: contact@akretion.com | "
            "Website: http://www.example.com",
        )
        self.assertEqual(company.email, "info@yourcompany.example.com")
