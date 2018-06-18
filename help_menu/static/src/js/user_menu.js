odoo.define('help_menu.UserMenu', function (require) {
    "use strict";

    var UserMenu = require('web.UserMenu');

    UserMenu.include({
        _onMenuHelp: function () {
            var self = this;

            // Retrieves the action and executes it
            self._rpc({
                route: "/web/action/load",
                params: {
                    action_id: "help_menu.url_action"
                }
            }).then(function (action) {
                return self.do_action(action);
            });
        },
    });

});