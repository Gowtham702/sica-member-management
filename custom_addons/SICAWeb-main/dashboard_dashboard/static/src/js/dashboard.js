odoo.define('custom_dashboard.dashboard_action', function (require){
"use strict";
var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var QWeb = core.qweb;
var rpc = require('web.rpc');
var ajax = require('web.ajax');
var _t = core._t;
var session = require('web.session');


var CustomDashBoard = AbstractAction.extend({
   template: 'CustomDashBoard',

   events: {
             'click .member':'member',
             'click .mem_work':'mem_work',
             'click .sica_receipt':'sica_receipt',
             'click .other_receipt':'other_receipt',
             'click .cash_deposit':'cash_deposit',
             'click .expenses_mag':'expenses_mag',
             'click .cash_with':'cash_with',
             'click .exp_typ':'exp_typ',
             'click .mem_report':'mem_report',
             'click .sica_report':'sica_report',
             'click .cbt_report':'cbt_report',
             'click .other_report':'other_report',
             'click .exp_report':'exp_report',
             'click .sms_otp':'sms_otp',
             'click .payment_request':'payment_request',
             'click .member_payment':'member_payment',
             'click .diss_ctg_form':'diss_ctg_form',
             'click .diss_top_form':'diss_top_form',
             'click .diss_cmd':'diss_cmd',
             'click .gri_report':'gri_report',
             'click .gri_report_nw':'gri_report_nw',
             'click .dly_shut_update':'dly_shut_update',
             'click .proj_tit':'proj_tit',
             'click .shot_img':'shot_img',
             'click .shot_update':'shot_update',
             'click .dop_update':'dop_update',
             'click .job_post':'job_post',
             'click .mem_skill':'mem_skill',
             'click .job_provider':'job_provider',
             'click .job_seeker':'job_seeker',
             'click .banner_img':'banner_img',
             'click .format':'format',
             'click .ctg':'ctg',
             'click .event':'event',
             'click .spd_ctg':'spd_ctg',
             'click .spd_sub_ctg':'spd_sub_ctg',
             'click .spd_product':'spd_product',
             'click .spd_banner':'spd_banner',
             'click .gallery_ctg':'gallery_ctg',
             'click .gallery':'gallery',
             'click .gallery_comment':'gallery_comment',
             'click .tech_talk':'tech_talk',
             'click .Shooting diary List ':'Shooting diary List ',
             'click .sica_blog':'sica_blog',
             'click .sica_news':'sica_news',
             'click .open_setting':'open_setting',

             'click .today_birthday_emp':'today_birthday_emp',
    },

   init: function(parent, context) {
       this._super(parent, context);
       this.dashboards_templates = ['DashboardProject'];
       this.today_sale = [];
       this.today_birthday = [];
       this.tomorrow_birthday = [];
   },
       willStart: function() {
       var self = this;
       var def_group = session.user_has_group('base.group_system').then(function(has_group){
           self.is_system_user = has_group;
       });
       return $.when(ajax.loadLibs(this), this._super(), def_group).then(function() {
           return self.fetch_data();
       });
   },
   start: function() {
           var self = this;
           this.set("title", 'SICA Dashboard');
           return this._super().then(function() {
               self.render_dashboards();
           });
       },
       render_dashboards: function(){
       var self = this;
       _.each(this.dashboards_templates, function(template) {
           self.$('.o_pj_dashboard').append(QWeb.render(template, {widget: self}));
       });
   },
    fetch_data: function() {
           var self = this;
           var def1 =  this._rpc({
               model: 'res.member',
               method: 'get_tiles_data'
       }).then(function(result)
        {
          self.today_birthday = result['today_birthday'],
          self.tomorrow_birthday = result['tomorrow_birthday']
       });
           return $.when(def1);
       },

    member: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Member"),
            type: 'ir.actions.act_window',
            res_model: 'res.member',
            view_mode: 'kanban,tree,form',
            views: [[false, 'kanban'],[false, 'list'],[false, 'form']],
            domain: [['state','in',['active']]],
            target: 'current',
        }, options)

    },


    mem_work: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Member Work"),
            type: 'ir.actions.act_window',
            res_model: 'member.work',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    sica_receipt: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("SICA/CBT Receipts"),
            type: 'ir.actions.act_window',
            res_model: 'sica.cbt.receipt',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    other_receipt: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Other Receipts"),
            type: 'ir.actions.act_window',
            res_model: 'other.receipt',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    cash_deposit: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Cash Deposit"),
            type: 'ir.actions.act_window',
            res_model: 'cash.deposit',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    expenses_mag: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Expense"),
            type: 'ir.actions.act_window',
            res_model: 'member.expense',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    cash_with: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Cash Withdraw"),
            type: 'ir.actions.act_window',
            res_model: 'cash.withdraw',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    exp_typ: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Expense Type"),
            type: 'ir.actions.act_window',
            res_model: 'expense.type',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    mem_report: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Member Report"),
            type: 'ir.actions.act_window',
            res_model: 'res.member',
            view_mode: 'tree',
            views: [[false, 'list'], [false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    sica_report: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("SICA Receipt Report"),
            type: 'ir.actions.act_window',
            res_model: 'sica.receipt',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    cbt_report: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("CBT Receipt Report"),
            type: 'ir.actions.act_window',
            res_model: 'cbt.receipt',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    other_report: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Other Receipt Report"),
            type: 'ir.actions.act_window',
            res_model: 'other.receipt',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    exp_report: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Expense Report"),
            type: 'ir.actions.act_window',
            res_model: 'member.expense',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    sms_otp: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Sms Otp"),
            type: 'ir.actions.act_window',
            res_model: 'sms.otp',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    payment_request: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Payment Request"),
            type: 'ir.actions.act_window',
            res_model: 'member.payment.request',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    member_payment: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Member Payment"),
            type: 'ir.actions.act_window',
            res_model: 'member.payment',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    diss_ctg_form: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Discuss Category Forum"),
            type: 'ir.actions.act_window',
            res_model: 'discuss.category',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    diss_top_form: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Discuss Topic Forum"),
            type: 'ir.actions.act_window',
            res_model: 'discussion.forum',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    diss_cmd: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Discussion Comment"),
            type: 'ir.actions.act_window',
            res_model: 'discussion.comment',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    gri_report: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Grievance Reason"),
            type: 'ir.actions.act_window',
            res_model: 'grievance.reason',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    gri_report_nw: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Grievance Report"),
            type: 'ir.actions.act_window',
            res_model: 'grievance.report',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    dly_shut_update: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Daily Shooting Update"),
            type: 'ir.actions.act_window',
            res_model: 'daily.shooting.update',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    proj_tit: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Project Title"),
            type: 'ir.actions.act_window',
            res_model: 'shooting.title',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    shot_img: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Shooting Image"),
            type: 'ir.actions.act_window',
            res_model: 'shooting.image',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    shot_update: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Shooting Update"),
            type: 'ir.actions.act_window',
            res_model: 'sica.shooting',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    dop_update: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("DOP Update"),
            type: 'ir.actions.act_window',
            res_model: 'shooting.dop',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    job_post: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Job Post"),
            type: 'ir.actions.act_window',
            res_model: 'job.title',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    mem_skill: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Member Skill"),
            type: 'ir.actions.act_window',
            res_model: 'member.skill',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    job_provider: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Job Provider"),
            type: 'ir.actions.act_window',
            res_model: 'member.job.provider',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    job_seeker: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Job Seeker"),
            type: 'ir.actions.act_window',
            res_model: 'member.job.seeker',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    banner_img: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Banner Image"),
            type: 'ir.actions.act_window',
            res_model: 'mobile.photo',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    format: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Format"),
            type: 'ir.actions.act_window',
            res_model: 'member.medium',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    ctg: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Category"),
            type: 'ir.actions.act_window',
            res_model: 'event.category',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    event: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Event"),
            type: 'ir.actions.act_window',
            res_model: 'shooting.event',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    spd_ctg: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("SPD Category"),
            type: 'ir.actions.act_window',
            res_model: 'spd.category',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    spd_sub_ctg: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("SPD Sub Category"),
            type: 'ir.actions.act_window',
            res_model: 'spd.sub.category',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    spd_product: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("SPD Product"),
            type: 'ir.actions.act_window',
            res_model: 'spd.product',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    spd_banner: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("SPD Banner"),
            type: 'ir.actions.act_window',
            res_model: 'spd.banner.photo',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    gallery_ctg: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Gallery Category"),
            type: 'ir.actions.act_window',
            res_model: 'sica.gallery.category',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    gallery: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Gallery"),
            type: 'ir.actions.act_window',
            res_model: 'sica.gallery',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    gallery_comment: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Gallery Comment"),
            type: 'ir.actions.act_window',
            res_model: 'gallery.comment',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    tech_talk: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Tech Talk"),
            type: 'ir.actions.act_window',
            res_model: 'tech.talk',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    sica_blog: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Sica Blog"),
            type: 'ir.actions.act_window',
            res_model: 'sica.blog',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    sica_news: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.do_action({
            name: _t("Sica News"),
            type: 'ir.actions.act_window',
            res_model: 'sica.news',
            view_mode: 'tree',
            views: [[false, 'list'],[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },

    open_setting: function () {
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
//        this.do_action({
//            name: _t("Setting"),
//            type: 'ir.actions.act_url',
//            url: '/web#cids=1&menu_id=97&action=327&model=res.config.settings&view_type=form',
//            target: 'current',
//        }, options)
        this.do_action({
            name: _t("Setting"),
            type: 'ir.actions.act_window',
            res_model: 'res.config.settings',
            view_mode: 'form',
            views: [[false, 'form']],
            domain: [],
            target: 'current',
        }, options)

    },






    })
core.action_registry.add('custom_dashboard_tags', CustomDashBoard);
return CustomDashBoard;
})