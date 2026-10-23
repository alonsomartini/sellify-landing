/* Sellify: script compartido por / (español) y /en/ (inglés) */
(function(){
  var lang = document.documentElement.lang === 'en' ? 'en' : 'es';
  var T = {
    es: { intro: 'Hola Alonso, quiero agendar una auditoría.', name: 'Nombre', email: 'Email', brand: 'Marca', market: 'Vendo en' },
    en: { intro: "Hi Alonso, I'd like to book an audit.", name: 'Name', email: 'Email', brand: 'Brand', market: 'Selling on' }
  }[lang];

  // Selector ES/EN: recuerda la elección para que la detección automática no la pise
  document.querySelectorAll('[data-set-lang]').forEach(function(a){
    a.addEventListener('click', function(){
      document.cookie = 'lang=' + a.getAttribute('data-set-lang') + '; path=/; max-age=31536000; SameSite=Lax';
    });
  });

  // Formulario: abre WhatsApp Business con los datos (sin backend)
  var form = document.getElementById('audit-form');
  if (form) {
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var d = new FormData(form);
      var msg = T.intro + '\n' +
        T.name + ': ' + (d.get('nombre') || '') + '\n' +
        T.email + ': ' + (d.get('email') || '') + '\n' +
        T.brand + ': ' + (d.get('marca') || '-') + '\n' +
        T.market + ': ' + (d.get('mercado') || '');
      window.open('https://wa.me/34627071754?text=' + encodeURIComponent(msg), '_blank', 'noopener');
    });
  }

  // Video de Tatiana: el botón de play solo aparece si el archivo existe
  var card = document.getElementById('video-card');
  var dialog = document.getElementById('video-dialog');
  var video = document.getElementById('video-el');
  if (card && dialog && video) {
    fetch('/assets/tatiana-testimonio.mp4', { method: 'HEAD' }).then(function(r){
      if (!r.ok) return;
      card.disabled = false;
      card.classList.add('has-video');
      card.addEventListener('click', function(){ dialog.showModal(); video.play(); });
    }).catch(function(){});
    var closeVideo = function(){ video.pause(); dialog.close(); };
    document.getElementById('video-close').addEventListener('click', closeVideo);
    dialog.addEventListener('click', function(e){ if (e.target === dialog) closeVideo(); });
    dialog.addEventListener('close', function(){ video.pause(); });
  }
})();
