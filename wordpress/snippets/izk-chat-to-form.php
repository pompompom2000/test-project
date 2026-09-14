<?php
/**
 * 石名坂：チャットの会話を、お問い合わせフォームの本文に引き継ぐ
 *
 * 使い方は2つに分かれます。
 *
 * 1) チャットボットの設定「Compliance Text」に、次の1行を入れる。
 *      <a href="/contact/" class="izk-to-form">この会話をお問い合わせに送る</a>
 *    ここはAI Engineが HTML をそのまま表示する欄なので、
 *    プラグインの構造をいじらずにリンクを置けます。
 *
 * 2) このスニペットを WPCode に「PHPスニペット」で入れ、「どこでも実行」で有効化する。
 *
 * 動き
 *   ・上のリンクが押されたら、その時点のチャットの会話を読み取って
 *     ブラウザに一時保存し、お問い合わせページへ移動します。
 *   ・お問い合わせページで、本文欄にその会話を貼り付けます。
 *   ・送信ボタンはお客様に押していただきます。自動送信はしません。
 *
 * 壊れ方について
 *   会話が読み取れなかった場合は、何も保存せずに、ただのリンクとして
 *   お問い合わせページへ移動します。「押しても何も起きない」状態にはなりません。
 *   AI Engine の更新でクラス名が変わったときは、この形で表に出ます。
 */

add_action( 'wp_footer', function () {

	if ( is_admin() ) {
		return;
	}
	?>
<script id="izk-chat-to-form" data-noptimize="1">
(function () {
	'use strict';

	// AI Engine 側のクラス名。更新で変わったらここだけ直す
	var SEL_CONVERSATION = '.mwai-conversation';
	var SEL_MESSAGE      = '.mwai-reply';
	var CLASS_AI         = 'mwai-ai';
	var CLASS_USER       = 'mwai-user';

	var STORE_KEY   = 'izkChatTranscript';
	var LINK_CLASS  = 'izk-to-form';
	var CONTACT_PATH = '/contact/';
	var HEADING     = '──── チャットでのやりとり ────';

	function store() {
		try {
			return window.sessionStorage;
		} catch (e) {
			return null;
		}
	}

	/** チャットの会話を文章にする。読めなければ空文字を返す */
	function readTranscript() {
		var box = document.querySelector(SEL_CONVERSATION);
		if (!box) { return ''; }

		var nodes = box.querySelectorAll(SEL_MESSAGE);
		var lines = [];

		for (var i = 0; i < nodes.length; i++) {
			var el = nodes[i];
			var who;
			if (el.classList.contains(CLASS_USER)) {
				who = 'お客様';
			} else if (el.classList.contains(CLASS_AI)) {
				who = '案内係';
			} else {
				continue; // system や error は入れない
			}
			var text = (el.innerText || el.textContent || '')
				.replace(/\u00a0/g, ' ')
				.replace(/[ \t]+\n/g, '\n')
				.replace(/\n{3,}/g, '\n\n')
				.trim();
			if (text) {
				lines.push(who + '：' + text);
			}
		}

		// お客様の発言が1つもなければ、引き継ぐ意味がない
		var hasUser = lines.some(function (l) { return l.indexOf('お客様：') === 0; });
		if (!hasUser) { return ''; }

		return lines.join('\n\n');
	}

	/** 本文欄に収まる長さに整える。古いやりとりから削る */
	function fit(transcript, room) {
		var head = HEADING + '\n\n';
		var tail = '\n\n──── ここまで ────';
		var budget = room - head.length - tail.length;
		if (budget < 200) { return ''; }

		if (transcript.length > budget) {
			var note = '（前半のやりとりは省略しています）\n\n';
			transcript = note + transcript.slice(transcript.length - (budget - note.length));
		}
		return head + transcript + tail;
	}

	// ── 1. リンクが押されたら会話を保存する ────────────────
	document.addEventListener('click', function (ev) {
		var link = ev.target && ev.target.closest
			? ev.target.closest('a.' + LINK_CLASS)
			: null;
		if (!link) { return; }

		var s = store();
		if (!s) { return; }           // 保存できなくても、リンクとしては動く

		var transcript = readTranscript();
		try {
			if (transcript) {
				s.setItem(STORE_KEY, transcript);
			} else {
				s.removeItem(STORE_KEY);
			}
		} catch (e) { /* 保存できなければ、そのまま移動する */ }
	}, true);

	// ── 2. お問い合わせページで本文欄に貼り付ける ──────────
	function paste() {
		if (location.pathname.indexOf(CONTACT_PATH) !== 0) { return; }

		var s = store();
		if (!s) { return; }

		var transcript;
		try {
			transcript = s.getItem(STORE_KEY);
		} catch (e) { return; }
		if (!transcript) { return; }

		var field = document.querySelector('textarea[name="your-message"]');
		if (!field) { return; }

		try { s.removeItem(STORE_KEY); } catch (e) {}

		var max = parseInt(field.getAttribute('maxlength'), 10);
		if (!max || max < 1) { max = 2000; }

		var before = field.value || '';
		var room = max - before.length - (before ? 2 : 0);
		var block = fit(transcript, room);
		if (!block) { return; }

		var after = before ? (before.replace(/\s+$/, '') + '\n\n' + block) : block;
		field.value = after;
		field.dispatchEvent(new Event('input', { bubbles: true }));

		notice(field, before);
	}

	/** 貼り付けたことを知らせる。元に戻せるようにする */
	function notice(field, previous) {
		if (document.getElementById('izk-paste-notice')) { return; }

		var box = document.createElement('div');
		box.id = 'izk-paste-notice';
		box.setAttribute('role', 'status');
		box.style.cssText = 'margin:12px 0;padding:12px 14px;border-left:4px solid #b34a18;'
			+ 'background:#f6e5db;color:#25231e;font-size:14px;line-height:1.7;border-radius:2px;';

		var msg = document.createElement('span');
		msg.textContent = 'チャットでのやりとりを、下の「お問い合わせ内容」に貼り付けました。'
			+ '内容をご確認のうえ、必要なところを書き足して送信してください。';
		box.appendChild(msg);

		var undo = document.createElement('button');
		undo.type = 'button';
		undo.textContent = '貼り付けをやめる';
		undo.style.cssText = 'margin-left:10px;padding:4px 12px;font:inherit;font-size:13px;'
			+ 'border:1px solid #b34a18;background:#fff;color:#b34a18;border-radius:2px;cursor:pointer;';
		undo.addEventListener('click', function () {
			field.value = previous;
			field.dispatchEvent(new Event('input', { bubbles: true }));
			box.remove();
		});
		box.appendChild(undo);

		// 「お問い合わせ内容」の見出しの上に出す。段落の外に置いて、体裁を崩さない
		var label = field.id ? document.querySelector('label[for="' + field.id + '"]') : null;
		var anchor = (label && label.closest('p'))
			|| field.closest('p')
			|| field.closest('.wpcf7-form-control-wrap')
			|| field;
		anchor.parentNode.insertBefore(box, anchor);
		if (typeof box.scrollIntoView === 'function') {
			box.scrollIntoView({ block: 'center' });
		}
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', paste);
	} else {
		paste();
	}
})();
</script>
	<?php
}, 99 );
