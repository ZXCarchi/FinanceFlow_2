(() => {
  const open = (id) => {
    const modal = document.getElementById(id);
    if (modal) { modal.classList.remove('hidden'); document.body.style.overflow='hidden'; }
  };
  const close = (modal) => {
    if (modal) { modal.classList.add('hidden'); document.body.style.overflow=''; }
  };
  document.addEventListener('click', (e) => {
    const opener = e.target.closest('[data-open-modal]');
    if (opener) open(opener.dataset.openModal);
    if (e.target.closest('[data-close-modal]')) close(e.target.closest('[data-modal]'));
    if (e.target.matches('[data-modal]')) close(e.target);
  });
  document.querySelectorAll('form[data-confirm]').forEach(form => form.addEventListener('submit', e => {
    if (!confirm(form.dataset.confirm)) e.preventDefault();
  }));

  const coachForm = document.getElementById('coachForm');
  if (coachForm) {
    const input = document.getElementById('coachInput');
    const log = document.getElementById('chatLog');
    const token = coachForm.querySelector('[name=csrfmiddlewaretoken]').value;
    const addBubble = (text, who) => { const div=document.createElement('div'); div.className=`bubble ${who}`; div.textContent=text; log.appendChild(div); log.scrollTop=log.scrollHeight; };
    const ask = async (message) => {
      if (!message.trim()) return;
      addBubble(message,'user'); input.value=''; input.disabled=true;
      try {
        const r=await fetch(coachForm.dataset.url,{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':token},body:JSON.stringify({message})});
        const data=await r.json(); addBubble(data.reply,'bot');
      } catch { addBubble(coachForm.dataset.error || 'The coach could not respond right now.','bot'); }
      finally { input.disabled=false; input.focus(); }
    };
    coachForm.addEventListener('submit',e=>{e.preventDefault();ask(input.value)});
    document.querySelectorAll('[data-prompt]').forEach(btn=>btn.addEventListener('click',()=>ask(btn.dataset.prompt)));
  }

  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js').catch(()=>{});
})();
