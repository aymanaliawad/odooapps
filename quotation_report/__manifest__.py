{
    'name': 'Quotation Report',
    'version': '1.5',
    'category': '',
    "sequence": 15,
    'category': 'Sales Report',
    'description': """
     *  This module contain sales report.
    """,
    'depends': ['base', 'web', 'sale', 'account'],
    'init_xml': [],
    'data': [

        'views/res_company_inherit.xml',
        'reports/quotation_report.xml',
        'reports/invoice_report.xml'


    ],
    'demo_xml': [],
    'test': [
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}