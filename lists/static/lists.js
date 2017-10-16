window.Superlists = {};
window.Superlists.initialize = function() {
  $("input[name='text']").on('keypress', function() {
    $(".has-error").hide();
  });
};


/* vim:set sw=2:et:sts=-1: */
