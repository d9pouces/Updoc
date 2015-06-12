df.connect('updoc.delete_doc_info', function (options) {
    "use strict";
    $('.updoc_' + options.doc_id).remove();
});