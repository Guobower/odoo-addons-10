odoo.define('help_menu.UserMenu', function (require) {
    "use strict";

    var UserMenu = require('web.UserMenu');

    UserMenu.include({
        on_menu_help: function () {
            var self = this;

            // Retrieves the action and executes it
            self.rpc("/web/action/load", {action_id: "help_menu.url_action"}).then(function (action) {
                return self.do_action(action);
            });
        },
    });

});