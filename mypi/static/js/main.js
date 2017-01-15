/**
 * Mypi
 */
var API_VERSION = '';

function __() {
    return arguments[0]
}

function msgprint(params) {
    var message = typeof data === "string" ? params : params.message;
    alert(message);
    return;

    function getDialogMarkup() {
        return '<dialog class="mdl-dialog"> \
    <h4 class="mdl-dialog__title"></h4> \
    <div class="mdl-dialog__content"> \
    </div> \
    <div class="mdl-dialog__actions"> \
      <button type="button" class="mdl-button button-yes">OK</button>  \
      <button type="button" class="mdl-button button-close">Close</button> \
    </div> \
  </dialog>'
    }

    var $dialog = $('dialog');
    if (!$dialog.length) {
        $dialog = $(getDialogMarkup()).appendTo('body')
    }

    $dialog.find('.mdl-dialog__title').text(params.title);
    $dialog.find('.mdl-dialog__content').html(params.message);
}
var Page = {};

Page['Home'] = {
    init: function () {
        var $memoryProgress = $('#memory-progress'), $memoryInfo = $('#memory-info'), $cpuInfo = $('#cpu-info');

        Application.call({
            cmd: 'device.system_info',
            callback: function (data) {
                var p = $memoryProgress.get(0)

                if (!$memoryProgress.hasClass('is-upgraded')) {
                    $memoryProgress.addClass('mdl-js-progress');
                    componentHandler.upgradeElement(p);
                }

                p.MaterialProgress.setProgress(data.memory.percent);
                delete data.memory.percent

                var list = [], cpus = [];
                $.each(data.memory, function (k, val) {
                    list.push(
                        '<div class="mdl-list__item">\
    <span class="mdl-list__item-primary-content">\
      <span class="mdl-typography--text-capitalize">' + k + '</span>\
    </span>\
    <span class="mdl-list__item-secondary-action">' + val + '</span>\
  </div>'
                    )
                })

                $memoryInfo.html(list.join(''))

                $.each(data.cpus, function (k, val) {
                    var div = document.createElement('div')
                    div.className = 'mdl-progress mdl-js-progress';
                    componentHandler.upgradeElement(div);
                    div.MaterialProgress.setProgress(val);
                    document.getElementById('cpu-info').appendChild(div);
                })

                var $memCard = $memoryInfo.closest('.mdl-card'),
                    $cpuCard = $cpuInfo.closest('.mdl-card');

                $cpuCard.ready(function () {
                    if ($memCard.height() > $cpuCard.height()) {
                        $cpuCard.css('height', $memCard.height() + 'px')
                    }
                })
            }
        })
    }
}

var Application = {
    init: function () {
        $('[data-cmd]', 'body').on('click', function (e) {
            var $this = $(this), data = $this.data()
            if (data.confirm) {
                if (confirm(data.confirm)) {
                    delete data.confirm
                    Application.call(data)
                }
            } else {
                Application.call(data)
            }
        })

        Page.Home.init()
    },

    call: function (opts) {
        if (!opts.args) {
            opts.args = {}
        }

        if (opts.cmd) {
            opts.url = '/cmd'
            opts.args['cmd'] = opts.cmd
        }

        // stringify args if required
        for (key in opts.args) {
            if (opts.args[key] && ($.isPlainObject(opts.args[key]) || $.isArray(opts.args[key]))) {
                opts.args[key] = JSON.stringify(opts.args[key]);
            }
        }

        // no cmd?
        if (!opts.args.cmd && !opts.url) {
            console.log(opts)
            throw "Incomplete Request";
        }

        var statusCode = {
            200: function (data, xhr) {
                opts.callback && opts.callback(data, xhr.responseText);
            },
            401: function (xhr) {
                msgprint({message: __("You have been logged out"), indicator: 'red'});
            },
            404: function (xhr) {
                msgprint({
                    title: __("Not found"), indicator: 'red',
                    message: __('The resource you are looking for is not available')
                });
            },
            403: function (xhr) {
                msgprint({
                    title: __("Not permitted"), indicator: 'red',
                    message: __('You do not have enough permissions to access this resource. Please contact your manager to get access.')
                });
            },
            508: function (xhr) {
                msgprint({
                    title: __('Please try again'), indicator: 'red',
                    message: __("Another transaction is blocking this one. Please try again in a few seconds.")
                });
            },
            413: function (data, xhr) {
                msgprint({
                    indicator: 'red',
                    title: __('File too big'),
                    message: __("File size exceeded the maximum allowed size of {0} MB",
                        [(frappe.boot.max_file_size || 5242880) / 1048576])
                });
            },
            417: function (xhr) {
                var r = xhr.responseJSON;
                if (!r) {
                    try {
                        r = JSON.parse(xhr.responseText);
                    } catch (e) {
                        r = xhr.responseText;
                    }
                }

                opts.error_callback && opts.error_callback(r);
            },
            501: function (data, xhr) {
                if (typeof data === "string") data = JSON.parse(data);
                opts.error_callback && opts.error_callback(data, xhr.responseText);
            },
            500: function (xhr) {
                msgprint({
                    message: __("Server Error: Please check your server logs or contact tech support."),
                    title: __('Something went wrong'),
                    indicator: 'red'
                });
                opts.error_callback && opts.error_callback();
                frappe.request.report_error(xhr, opts);
            },
            504: function (xhr) {
                msgprint(__("Request Timed Out"))
                opts.error_callback && opts.error_callback();
            }
        };

        return $.ajax({
            url: (API_VERSION ? '/' + API_VERSION + opts.url : opts.url),
            type: opts.type || 'POST',
            dataType: opts.dataType || 'json',
            data: opts.args,
            cache: false
        })
            .done(function (data, textStatus, xhr) {
                if (typeof data === "string") data = JSON.parse(data);

                // callbacks
                var status_code_handler = statusCode[xhr.statusCode().status];
                if (status_code_handler) {
                    status_code_handler(data, xhr);
                }
            })
            .always(function (data, textStatus, xhr) {
                if (typeof data === "string") {
                    data = JSON.parse(data);
                }

                if (data.responseText) {
                    data = JSON.parse(data.responseText);
                }

                if (opts.always) {
                    opts.always(data);
                }
            })
            .fail(function (xhr, textStatus) {
                var status_code_handler = statusCode[xhr.statusCode().status];
                if (status_code_handler) {
                    status_code_handler(xhr);
                } else {
                    // if not handled by error handler!
                    opts.error_callback && opts.error_callback(xhr);
                }
            });
    }
}

$(document).ready(function () {
    Application.init()
})