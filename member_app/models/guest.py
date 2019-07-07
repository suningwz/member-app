import time
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import except_orm, ValidationError
from odoo.tools import misc, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo import http


class RegisterGuest(models.Model):
    _name = 'register.guest'
    _description = 'Register Guest'

    @api.multi
    def name_get(self):
        if not self.ids:
            return []
        res = []
        for field6 in self.browse(self.ids):
            partner = str(field6.partner_id.name)
            res.append((field6.id, partner))
        return res

    _sql_constraints = [
        ('partner_id_unique',
         'UNIQUE(partner_id)',
         'Partner Name must be unique')
    ]
    @api.onchange('partner_id')
    def _get_state(self):
        for r in self.partner_id:
            #  r=rec.partner_id.id
            street = r.street
            country = r.country_id.id
            city = r.city
            #  city=r.city
            post = r.function
            phone = r.phone
            state = r.state_id
            title = r.title.id
            email = r.email
            image = r.image
            self.country_id = country
            self.state_id = state
            self.city = city
            self.phone = phone
            self.title = title
            self.image = image
            self.occupation = post
            self.email = email

    image = fields.Binary(
        "Image",
        attachment=True,
        help="This field holds the image used as avatar for this contact, \
         limited to 1024x1024px",
    )
    image_medium = fields.Binary(
        "Medium-sized image",
        attachment=True,
        help="Medium-sized image of this contact. It is automatically "
        "resized as a 128x128px image, with aspect ratio preserved. "
        "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized image",
        attachment=True,
        help="Small-sized image of this contact. It is automatically "
        "resized as a 64x64px image, with aspect ratio preserved. "
        "Use this field anywhere a small image is required.")
    partner_id = fields.Many2one(
        'res.partner', 'Name', domain=[
            ('is_member', '=', True)])
    city = fields.Char('City')
    street = fields.Char('Street')
    url = fields.Char('Website')
    phone = fields.Char('Phone')
    state_id = fields.Many2one('res.country.state', store=True)
    country_id = fields.Many2one('res.country', 'Country', store=True)
    dob = fields.Datetime('Date Of Birth', required=True)
    email = fields.Char('Email', required=True, store=True)
    occupation = fields.Char('Job title')
    nok = fields.Many2one('res.partner', 'Next of Kin', store=True)
    title = fields.Many2one('res.partner.title', 'Title', store=True)
    sponsor = fields.Many2one(
        'member.app',
        string='Parent Member',
        required=True)
    account_id = fields.Many2one('account.account', 'Account')
    invoice_id = fields.Many2one('account_id', 'Invoice', store=True)

    product_id = fields.Many2one(
        'product.product', string='Membership type', domain=[
            ('membershipx', '=', True)], required=False)
    member_price = fields.Float(
        string='Section Cost',
        required=True,
        readonly=False)
    total = fields.Integer('Total Amount', default=60000, required=True)#compute='get_totals')
    date_order = fields.Datetime('Offer Date', default=fields.Datetime.now())
    member_age = fields.Integer(
        'Age',
        required=True,
        compute="get_duration_age")
    subscription = fields.Many2many(
        'subscription.payment',
        readonly=False,
        string='Add Sections',
        compute='get_package_cost')

    #  ,compute='get_all_packages')
    package = fields.Many2many('package.model', string='Compulsory Packages')
    package_cost = fields.Float(
        'Package Cost',
        required=False,
        compute='get_package_cost')
    users_followers = fields.Many2many('res.users', string='Add followers')

    #  3333
    place_of_work = fields.Char('Name of Work Place')
    work_place_manager_name = fields.Char('Name of Work Place')
    email_work = fields.Char('Work Place Email', required=True)
    binary_attach_letter = fields.Binary('Attach Verification Letter')
    binary_fname_letter = fields.Char('Binary Letter')
    address_work = fields.Text('Work Address')

    binary_attach_receipt = fields.Binary('Attach Payment Teller')
    binary_fname_receipt = fields.Char('Binary receipt')
    
    
    purpose_visit = fields.Text('Purpose of Visit')
    abroad_address = fields.Text('Address abroad')
    passport_number = fields.Char('Passport Number')
    
    resident_permit = fields.Char('Resident Permit Number')
    position_holder = fields.Char('Position in Company')
    
    member_condition = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
        ], 'Have you ever been a member of Ikoyi Club 1938', default='no', index=True, required=False, readonly=False, \
        copy=False, track_visibility='always')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('honourary', 'Honorary Secretary'),
        ('invoice', 'Invoicing'),
        ('wait', 'Waiting'),
        ('general_manager', 'General Manager'),
        ('honourary_two', 'Honorary Secretary'),
        ('verify', 'Verification'),
        ('confirm', 'Confirmed'),
    ], 'Status', default='draft', index=True, required=True, readonly=False,
                              copy=False, track_visibility='always')
    relationship = fields.Selection([('Child',
                                      'Child'),
                                     ('Brother',
                                      'Brother'),
                                     ('Sister',
                                      'Sister'),
                                     ('Friend',
                                      'Friend'),
                                     ('Spouse',
                                      'Spouse'),
                                     ],
                                    'Sponsor Relationship',
                                    index=True,
                                    required=True,
                                    readonly=False,
                                    copy=False,
                                    track_visibility='always')

    '''@api.model
    def create(self, vals):
        res = super(RegisterSpouseMember, self).create(vals)
        partner_id = vals.get('partner_id')
        partner = self.env['res.partner'].search([('id','=',partner_id)])
        if partner:
            partner.write({'is_member':True})
        return res'''

    '''@api.onchange('sponsor')
    def change_details(self):
        for rec in self:
            for fec in rec.sponsor:
                lists = []
                for tec in fec.subscription:
                    lists.append(tec.id)
                rec.subscription = [(6,0,lists)]'''

    '''@api.depends('product_id')
    def get_section_member_price(self):
        total = 0.00
        for rem in self:
            total = rem.product_id.list_price
            rem.member_price = total'''

    @api.depends('dob')
    def get_duration_age(self):
        for rec in self:
            start = rec.dob
            end = fields.Datetime.now()
            if start and end:
                server_dt = DEFAULT_SERVER_DATETIME_FORMAT
                strt = datetime.strptime(start, server_dt)
                ends = datetime.strptime(end, server_dt)
                durations = ends - strt
                rec.member_age = durations.days / 365

    @api.multi
    @api.depends('member_price', 'package_cost')
    def get_totals(self):
        for rec in self:
            rec.total = rec.member_price + rec.package_cost
    @api.one
    @api.depends('package', 'subscription')
    def get_package_cost(self):
        total1 = 0.0
        total2 = 0.
        for ret in self.package:
            total1 += ret.package_cost

        for rm in self.subscription:
            total2 += rm.member_price
        self.member_price = total2
        self.package_cost = total1

    @api.multi
    def button_send_hon(self):  # draft memoffice
        self.write({'state': 'honourary'})
        self.fetch_followers()
        return self.send_honour_mail()

    def fetch_followers(self):
        group1 = self.env.ref('member_app.manager_member_ikoyi').id
        group2 = self.env.ref('member_app.membership_honour_ikoyi').id
        group3 = self.env.ref('ikoyi_module.gm_ikoyi').id
        group4 = self.env.ref('member_app.membership_officer_ikoyi').id
        groups_lists = [group1, group2, group3, group4]
        groups_obj = self.env['res.groups']
        users = []
        for each in groups_lists:
            group_users = groups_obj.search([('id', '=', each)])
            if group_users:
                for user in group_users.users:
                    users.append(user.id)
                    self.users_followers = [(6, 0, users)]
            else:
                pass

    @api.multi
    def send_honour_mail(self, force=False):
        email_from = self.env.user.company_id.email
        group_user_id = self.env.ref('member_app.membership_honour_ikoyi').id
        extra_user = self.env.ref('member_app.manager_member_ikoyi').id
        groups = self.env['res.groups']
        group_users = groups.search([('id', '=', extra_user)])
        group_emails = group_users.users[1]
        extra = group_emails.login

        bodyx = "Sir/Madam, </br>We wish to notify you that a guest with name:\
         {} applies for guest membership on the date: {}.</br>\
             Kindly <a href={}> </b>Click <a/> to Login to the ERP to view \
        </br> Thanks".format(self.partner_id.name, fields.Datetime.now(),
                             self.get_url(self.id, self._name))
        self.mail_sending(email_from, group_user_id, extra, bodyx)

    # # # # # # # # # # # # # # # # # # # # # # # # #
    @api.multi
    def button_send_hon_invocie(self):  # honourary memberhou sec
        self.write({'state': 'invoice'})
        return self.send_memofficer_mail()

    @api.multi
    def send_memofficer_mail(self, force=False):
        email_from = self.env.user.company_id.email
        group_user_id = self.env.ref('member_app.membership_officer_ikoyi').id
        extra_user = self.env.ref('member_app.manager_member_ikoyi').id
        groups = self.env['res.groups']
        group_users = groups.search([('id', '=', extra_user)])
        group_emails = group_users.users[1]
        extra = group_emails.login

        bodyx = "Sir/Madam, </br>I wish to notify you that a request for guest \
         membership with name: {} have been approve on the date: {}.</br>\
             Kindly <a href={}> </b>Click <a/> to Login to the \
             ERP to view</br> Thanks".format(self.partner_id.name, fields.Datetime.now(), self.get_url(self.id, self._name))
        self.mail_sending(email_from, group_user_id, extra, bodyx)

    # # # # # # # # # # # # # # # # # # # # # # # # #
    @api.multi
    def button_send_invocie_wait(self):  # invoice memberofficer
        self.write({'state': 'wait'})
        self.send_mail_workplace()
        return self.create_invoice()

    @api.multi
    def send_mail_workplace(self, force=False):
        email_from = self.env.user.company_id.email
        mail_to = self.email_work
        subject = "Ikoyi Club Member Verification"
        bodyx = "This is a verification message to verify that {} is a noble employer in {}, if (or not) so, kindly indicate and give us a feedback \
        so that we could continue our processes. </br> For further enquires, kindly contact {} </br> {} </br>\
        Thanks".format(self.partner_id.name, self.place_of_work, self.env.user.company_id.name, self.env.user.company_id.phone)
        self.mail_sending_one(email_from, mail_to, bodyx, subject)
    # # # # # # # # # # # # # # # # # # # # # # # # # #

    @api.multi
    def button_send_gen_Manager(self):  # wait memberoficerc
        self.write({'state': 'general_manager'})
    # # # # # # # # # # # # # # # # # # # # # # # # # #

    @api.multi
    def button_gen_Manager_hon2(self):  # general_manager gm_ikoyi
        self.write({'state': 'honourary_two'})

    @api.multi
    def button_hon2_approve(self):  # honourary_two honsec
        self.write({'state': 'verify'})

    @api.multi
    def button_officer_confirm(self):  # verify memofficer
        self.write({'state': 'confirm'})
        self.send_mail_guest()

    @api.multi
    def send_mail_guest(self, force=False):
        email_from = self.env.user.company_id.email
        mail_to = self.email
        subject = "Ikoyi Club Guest Confirmation"
        bodyx = "This is a notification message that you have been confirmed as a guest of Ikoyi Club on the date: {}. </br> For further enquires,\
         kindly contact {} </br> {} </br>\
        Thanks".format(fields.Date.today(), self.env.user.company_id.name, self.env.user.company_id.phone)
        self.mail_sending_one(email_from, mail_to, bodyx, subject)

    @api.model
    def create(self, vals):
        res = super(RegisterGuest, self).create(vals)
        partner_id = vals.get('partner_id')
        partner = self.env['res.partner'].search([('id', '=', partner_id)])
        partner.write({'street': vals.get('street'),
                       'street2': vals.get('street'),
                       'email': vals.get('email'),
                       'state_id': vals.get('state_id'),
                       'title': vals.get('title'),
                       'image': vals.get('image'),
                       'phone': vals.get('phone'),
                       'function': vals.get('occupation')})
        return res

    @api.multi
    def create_invoice(self):  # invoice memoficer
        if self:
            invoice_list = self.create_membership_invoice()
            search_view_ref = self.env.ref(
                'account.view_account_invoice_filter', False)
            form_view_ref = self.env.ref('account.invoice_form', False)
            tree_view_ref = self.env.ref('account.invoice_tree', False)
            return {
                'domain': [('id', '=', self.invoice_id.id)],
                'name': 'Membership Invoices',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
                'search_view_id': search_view_ref and search_view_ref.id,
            }

    @api.multi
    def create_membership_invoice(self):
        """ Create Customer Invoice of Membership for partners.
        @param datas: datas has dictionary value which consist Id of Membership product and Cost Amount of Membership.
                      datas = {'membership_product_id': None, 'amount': None}
        """
        amount = self.total
        product = 0
        state_now = str(self.state).replace('_', ' ').capitalize()
        products = self.env['product.product']
        product_search = products.search(
            [('name', 'ilike', 'Guest Membership')])
        if product_search:
            #  product.append(product_search.id)
            product = product_search[0].id
        else:
            pro = products.create(
                {'name': 'Guest Membership', 'membershipx': True, 'list_price': amount})
            product = pro.id
        product_id = product
        self.write({'product_id': product})

        invoice_list = []
        branch_id = 0
        branch = self.env['res.branch']
        branch_search = branch.search([('name', 'ilike', 'Ikoyi Club Lagos')])
        if branch_search:
            branch_id = branch_search[0].id

        else:
            branch_create = branch.create(
                {'name': 'Ikoyi Club Lagos', 'company_id': self.env.user.company_id.id or 1})
            branch_id = branch_create.id

        for partner in self:
            invoice = self.env['account.invoice'].create({
                'partner_id': partner.partner_id.id,
                #  partner.partner_id.property_account_receivable_id.id,
                'account_id': partner.account_id.id,
                'fiscal_position_id': partner.partner_id.property_account_position_id.id,
                'branch_id': branch_id
            })
            line_values = {
                'product_id': product_id,  # partner.product_id.id,
                'price_unit': amount,
                'invoice_id': invoice.id,
                'account_id': partner.account_id.id or partner.partner_id.property_account_payable_id.id,

            }
            #  create a record in cache, apply onchange then revert back to a
            #  dictionnary
            invoice_line = self.env['account.invoice.line'].new(line_values)
            invoice_line._onchange_product_id()
            line_values = invoice_line._convert_to_write(
                {name: invoice_line[name] for name in invoice_line._cache})
            line_values['price_unit'] = amount
            invoice.write({'invoice_line_ids': [(0, 0, line_values)]})
            invoice_list.append(invoice.id)
            invoice.compute_taxes()

            partner.invoice_id = invoice.id

            find_id = self.env['account.invoice'].search(
                [('id', '=', invoice.id)])
            find_id.action_invoice_open()

        return invoice_list

    @api.multi
    def generate_receipt(self):  # verify,

        search_view_ref = self.env.ref(
            'account.view_account_invoice_filter', False)
        form_view_ref = self.env.ref('account.invoice_form', False)
        tree_view_ref = self.env.ref('account.invoice_tree', False)

        return {
            'domain': [('id', '=', self.invoice_id.id)],
            'name': 'Guest Membership Invoices',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            #  'views': [(form_view_ref.id, 'form')],
            'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
            'search_view_id': search_view_ref and search_view_ref.id,
        }

    @api.multi
    def see_breakdown_invoice(self):  # vis_account,

        search_view_ref = self.env.ref(
            'account.view_account_invoice_filter', False)
        form_view_ref = self.env.ref('account.invoice_form', False)
        tree_view_ref = self.env.ref('account.invoice_tree', False)

        return {
            'domain': [('id', '=', self.invoice_id.id)],
            'name': 'Guest Invoices',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            #  'views': [(form_view_ref.id, 'form')],
            'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
            'search_view_id': search_view_ref and search_view_ref.id,
        }

    def get_url(self, id, model):
        base_url = http.request.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        base_url += '/web# id=%d&view_type=form&model=%s' % (id, model)

    def mail_sending(self, email_from, group_user_id, extra, bodyx):
        from_browse = self.env.user.name
        groups = self.env['res.groups']
        for order in self:
            group_users = groups.search([('id', '=', group_user_id)])
            group_emails = group_users.users
            followers = []
            email_to = []
            for group_mail in self.users_followers:
                followers.append(group_mail.login)

            for gec in group_emails:
                email_to.append(gec.login)

            email_froms = str(from_browse) + " <" + str(email_from) + ">"
            mail_appends = (', '.join(str(item)for item in followers))
            mail_to = (','.join(str(item2)for item2 in email_to))
            subject = "Guest Membership Notification"

            extrax = (', '.join(str(extra)))
            followers.append(extrax)
            mail_data = {
                'email_from': email_froms,
                'subject': subject,
                'email_to': mail_to,
                'email_cc': mail_appends,  # + (','.join(str(extra)),
                'reply_to': email_from,
                'body_html': bodyx
            }
            mail_id = order.env['mail.mail'].create(mail_data)
            order.env['mail.mail'].send(mail_id)

    def mail_sending_one(self, email_from, mail_to, bodyx, subject):
        for order in self:
            mail_tos = str(mail_to)
            email_froms = "Ikoyi Club " + " <" + str(email_from) + ">"
            subject = subject
            mail_data = {
                'email_from': email_froms,
                'subject': subject,
                'email_to': mail_tos,
                #  'email_cc':,#  + (','.join(str(extra)),
                'reply_to': email_from,
                'body_html': bodyx
            }
            mail_id = order.env['mail.mail'].create(mail_data)
            order.env['mail.mail'].send(mail_id)
