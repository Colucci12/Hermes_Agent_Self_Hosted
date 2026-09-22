/*!
 * O grafo do Perlite faz window.open('/Nome-da-nota').
 * O unslug troca hífen por espaço, então "Bem-vindo" vira "Bem vindo"
 * e o conteúdo não carrega. Aqui o clique usa o caminho real da nota.
 */
(function () {
  var nativeOpen = window.open;
  window.open = function (url, target, features) {
    if (
      target === "_self" &&
      typeof url === "string" &&
      typeof getContent === "function"
    ) {
      var prefix = typeof uriPath === "string" ? uriPath : "/";
      var title = decodeURIComponent(String(url));
      if (title.indexOf(prefix) === 0) {
        title = title.slice(prefix.length);
      }
      title = title.replace(/^\/+/, "");
      var closeBtn = document.querySelector(
        '.view-header-nav-buttons[data-section="close"]'
      );
      if (closeBtn && window.getComputedStyle(closeBtn).display !== "none") {
        closeBtn.click();
      }
      getContent("/" + title);
      return window;
    }
    return nativeOpen.call(window, url, target, features);
  };
})();
