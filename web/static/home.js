
// Simple chat UI script for RAG frontend
(function(){
	// Config: change this to your RAG endpoint if needed
	const API_URL = '/api/ask'; // expects POST { question: string } -> { answer: string }

		const $messages = document.getElementById('messages');
	const $tpl = document.getElementById('tpl-message');
		const $form = document.getElementById('composer');
		const $input = document.getElementById('input');
		const $btnSend = document.getElementById('btnSend');
		// keep regenerate / clear if present elsewhere
		const $btnClear = document.getElementById('btnClear');
		const $btnRegenerate = document.getElementById('btnRegenerate');

	let lastQuestion = null;
	let lastAnswer = null;
	let currentRequest = null;

	function createMessage(who, text){
		const node = $tpl.content.cloneNode(true);
		const wrapper = node.querySelector('.msg');
		wrapper.classList.add(who === 'user' ? 'user' : 'assistant');
		node.querySelector('.who').textContent = who === 'user' ? 'You' : 'Assistant';
		node.querySelector('.bubble').textContent = text;
		return node;
	}

		function appendMessage(who, text){
			// ensure messages area visible
			const chatSection = document.getElementById('chat');
			if(chatSection && chatSection.hasAttribute('hidden')) chatSection.removeAttribute('hidden');
			const messageNode = createMessage(who, text);
			$messages.appendChild(messageNode);
			// scroll to bottom if overflow
			requestAnimationFrame(()=>{
				if($messages.scrollHeight > $messages.clientHeight){
					$messages.scrollTop = $messages.scrollHeight;
				}
			});
		}
	// Helper: convert plain text (with newlines and bullets) to safe HTML
	function formatTextToHTML(text){
		if(!text) return '';
		// escape HTML
		const esc = (s)=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
		const lines = esc(text).split(/\r?\n/);
		// detect list blocks
		let inList = false;
		const out = [];
		for(let line of lines){
			const trimmed = line.trim();
			if(trimmed.startsWith('- ') || trimmed.startsWith('* ')){
				if(!inList){ out.push('<ul>'); inList=true; }
				out.push('<li>'+trimmed.slice(2).trim()+'</li>');
			} else {
				if(inList){ out.push('</ul>'); inList=false; }
				if(trimmed===''){
					out.push('<p></p>');
				} else {
					out.push('<p>'+trimmed+'</p>');
				}
			}
		}
		if(inList) out.push('</ul>');
		return out.join('');
	}

	// Create a compact user pill element (like screenshot)
	function createUserPill(text){
		const wrap = document.createElement('div');
		wrap.className = 'user-pill';
		const avatar = document.createElement('div'); avatar.className='avatar'; avatar.textContent='F';
		const pill = document.createElement('div'); pill.className='mini-pill'; pill.textContent = text;
		wrap.appendChild(avatar); wrap.appendChild(pill);
		return wrap;
	}

	// Create assistant message node with actions
	function createAssistantNode(text){
		const wrap = document.createElement('div'); wrap.className='assistant-block';
		const bubble = document.createElement('div'); bubble.className='assistant-bubble';
		bubble.innerHTML = formatTextToHTML(text);
		wrap.appendChild(bubble);

		// actions row
		const actions = document.createElement('div'); actions.className='msg-actions';
		const copyBtn = document.createElement('button'); copyBtn.title='Copy'; copyBtn.textContent='📋';
		const likeBtn = document.createElement('button'); likeBtn.title='Like'; likeBtn.textContent='👍';
		const dislikeBtn = document.createElement('button'); dislikeBtn.title='Dislike'; dislikeBtn.textContent='👎';
		const retryBtn = document.createElement('button'); retryBtn.title='Retry'; retryBtn.textContent='Retry';
		actions.append(copyBtn, likeBtn, dislikeBtn, retryBtn);
		wrap.appendChild(actions);

		// handlers
		copyBtn.addEventListener('click', ()=>{
			const plain = text.replace(/\n/g,'\n');
			navigator.clipboard?.writeText(plain).then(()=>{
				copyBtn.textContent='Copied';
				setTimeout(()=>copyBtn.textContent='📋',1200);
			}).catch(()=>{});
		});
		likeBtn.addEventListener('click', ()=>{ likeBtn.classList.toggle('active'); });
		dislikeBtn.addEventListener('click', ()=>{ dislikeBtn.classList.toggle('active'); });
		retryBtn.addEventListener('click', ()=>{ regenerate(); });

		return wrap;
	}

	// Append DOM node to messages and reveal chat
	function appendNode(node){
		const chatSection = document.getElementById('chat');
		if(chatSection && chatSection.hasAttribute('hidden')) chatSection.removeAttribute('hidden');
		$messages.appendChild(node);
		requestAnimationFrame(()=>{ $messages.scrollTop = $messages.scrollHeight; });
	}

	function setLoading(on){
		if(on){
			$btnSend.disabled = true;
			$btnSend.innerHTML = '<span class="spinner"></span>';
		} else {
			$btnSend.disabled = false;
			$btnSend.textContent = 'Send →';
		}
	}
	function setLoading(on){
		if(on){
			$btnSend.disabled = true;
			$btnSend.innerHTML = '<span class="spinner"></span>';
		} else {
			$btnSend.disabled = false;
			$btnSend.textContent = '⬆';
		}
	}

		async function sendQuestion(text){
		if(!text || !text.trim()) return;
		lastQuestion = text;
			appendMessage('user', text);
			$input.value = '';
			setLoading(true);

		// If a request is ongoing, abort it
		if(currentRequest){
			try{ currentRequest.abort(); }catch(e){}
		}
		currentRequest = new AbortController();

		try{
					const resp = await fetch(API_URL, {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						signal: currentRequest.signal,
						body: JSON.stringify({ question: text })
					});

			if(!resp.ok){
				const textErr = await resp.text();
				appendMessage('assistant', `Error: ${resp.status} ${resp.statusText}\n${textErr}`);
				lastAnswer = null;
				return;
			}

			// try JSON first, fallback to plain text
			let data;
			try{ data = await resp.json(); }catch(e){ data = { answer: await resp.text() }; }

			const answer = (data && (data.answer || data.text || data.reply)) || JSON.stringify(data);
			appendMessage('assistant', answer);
			lastAnswer = answer;

		}catch(err){
			if(err.name === 'AbortError'){
				appendMessage('assistant','(request aborted)');
			} else {
				appendMessage('assistant', `Request failed: ${err.message}`);
				}
		} finally {
			setLoading(false);
			currentRequest = null;
		}
	}
	async function sendQuestion(text){
		if(!text || !text.trim()) return;
		lastQuestion = text;
		// add user pill
		const userPill = createUserPill(text);
		appendNode(userPill);
		$input.value = '';
		setLoading(true);

		// show big spinner while waiting
		const spinnerWrap = document.createElement('div'); spinnerWrap.className='waiting-spinner';
		const big = document.createElement('div'); big.className='big-spinner'; spinnerWrap.appendChild(big);
		appendNode(spinnerWrap);

		// If a request is ongoing, abort it
		if(currentRequest){
			try{ currentRequest.abort(); }catch(e){}
		}
		currentRequest = new AbortController();

		try{
			const resp = await fetch(API_URL, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				signal: currentRequest.signal,
				body: JSON.stringify({ question: text })
			});

			if(!resp.ok){
				const textErr = await resp.text();
				// replace spinner with error
				spinnerWrap.remove();
				const errNode = createAssistantNode(`Error: ${resp.status} ${resp.statusText}\n${textErr}`);
				appendNode(errNode);
				lastAnswer = null;
				return;
			}

			// try JSON first, fallback to plain text
			let data;
			try{ data = await resp.json(); }catch(e){ data = { answer: await resp.text() }; }

			const answer = (data && (data.answer || data.text || data.reply)) || JSON.stringify(data);
			// remove spinner and append assistant node
			spinnerWrap.remove();
			const assistantNode = createAssistantNode(answer);
			appendNode(assistantNode);
			lastAnswer = answer;


		}catch(err){
			spinnerWrap.remove();
			if(err.name === 'AbortError'){
				const abortNode = createAssistantNode('(request aborted)'); appendNode(abortNode);
			} else {
				const failNode = createAssistantNode(`Request failed: ${err.message}`); appendNode(failNode);
			}
		} finally {
			setLoading(false);
			currentRequest = null;
		}
	}

	// Regenerate uses lastQuestion
		function regenerate(){
		if(!lastQuestion) return;
		// Optionally remove last assistant reply before re-sending
		// Remove last assistant message node
		const msgs = Array.from($messages.children);
		for(let i=msgs.length-1;i>=0;i--){
			const el = msgs[i];
			if(el.classList.contains('assistant')){ el.remove(); break; }
			}
		sendQuestion(lastQuestion);
	}

	function clearChat(){
		$messages.innerHTML = '';
		lastQuestion = null; lastAnswer = null;
	}

	// events
		$form.addEventListener('submit', (e)=>{
			e.preventDefault();
			const text = $input.value;
			// visual feedback in hero: swap spinner to small spinning state
			sendQuestion(text);
		});

	$input.addEventListener('keydown', (e)=>{
		if(e.key === 'Enter' && !e.shiftKey){
			e.preventDefault();
			$form.dispatchEvent(new Event('submit', {cancelable:true}));
		}
	});

		if($btnClear) $btnClear.addEventListener('click', ()=>clearChat());
		if($btnRegenerate) $btnRegenerate.addEventListener('click', ()=>regenerate());

	// expose for debugging
	window.RAG_UI = { sendQuestion, regenerate, clearChat };

			// Keep the hero initial state (promo + spinner + heading) in HTML/CSS.
			// No additional mock messages here so the page looks like the screenshot until the user sends a question.

})();
