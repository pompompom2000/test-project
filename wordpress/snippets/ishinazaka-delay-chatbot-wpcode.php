<?php
/**
 * WPCode（コードスニペット）貼り付け用。
 *
 * 使い方: WPCode → 新規スニペット追加 → コードタイプ「PHPスニペット」→
 *         下の「=== ここから ===」以降を貼り付け → 挿入方法「自動挿入 / サイト全体で実行」→ 有効化。
 *
 * ※ WPCode の編集画面には <?php の行は入れません。
 *   このファイルは Git 上で色分け表示させるために先頭に <?php を付けています。
 */

// === ここから ===

// 何も操作されなくてもチャットを出すまでの待ち時間（ミリ秒）。0 = 操作があるまで出さない。
if ( ! defined( 'ISHINAZAKA_CHATBOT_DELAY_MS' ) ) {
	define( 'ISHINAZAKA_CHATBOT_DELAY_MS', 8000 );
}

// チャットを出すページを限定したい場合に指定する。空のままなら全ページで（遅延して）読み込む。
// 例: array( '/', '/saiseki-hanbai/', '/simulation/', '/faq/', '/contact/' )
if ( ! defined( 'ISHINAZAKA_CHATBOT_ONLY_PATHS' ) ) {
	define( 'ISHINAZAKA_CHATBOT_ONLY_PATHS', array() );
}

if ( ! function_exists( 'ishinazaka_chatbot_is_allowed_page' ) ) {
	function ishinazaka_chatbot_is_allowed_page() {
		$only = ISHINAZAKA_CHATBOT_ONLY_PATHS;
		if ( empty( $only ) ) {
			return true;
		}
		$path = isset( $_SERVER['REQUEST_URI'] ) ? wp_parse_url( $_SERVER['REQUEST_URI'], PHP_URL_PATH ) : '/';
		$path = trailingslashit( $path );
		foreach ( $only as $allowed ) {
			$allowed = trailingslashit( $allowed );
			if ( '/' === $allowed ) {
				if ( '/' === $path ) {
					return true;
				}
				continue;
			}
			if ( 0 === strpos( $path, $allowed ) ) {
				return true;
			}
		}
		return false;
	}
}

// 対象外のページでは、チャットのプログラムとCSSをそもそも読み込まない。
add_action( 'wp_enqueue_scripts', function () {
	if ( is_admin() || ishinazaka_chatbot_is_allowed_page() ) {
		return;
	}
	wp_dequeue_script( 'mwai_chatbot' );
	wp_deregister_script( 'mwai_chatbot' );
	foreach ( array( 'mwai_chatbot_theme_chatgpt', 'mwai_chatbot_theme_timeless', 'mwai_chatbot_theme_messages' ) as $style ) {
		wp_dequeue_style( $style );
	}
}, 100 );

// 対象ページでは、すぐ実行されない形に書き換えておく。
add_filter( 'script_loader_tag', function ( $tag, $handle, $src ) {
	if ( 'mwai_chatbot' !== $handle || is_admin() ) {
		return $tag;
	}
	// このコードが二重に読み込まれても壊れないよう、書き換え済みならそのまま返す。
	if ( false !== strpos( $tag, 'data-ishinazaka-delay-src' ) ) {
		return $tag;
	}
	// (?<![-\w]) は data-...-src= のような別属性に誤って一致させないための指定。
	return preg_replace(
		'/<script\b([^>]*?)(?<![-\w])src=/',
		'<script$1data-noptimize="1" type="text/plain" data-ishinazaka-delay-src=',
		$tag,
		1
	);
}, 20, 3 );

// 訪問者が操作したとき、または指定秒数後に、本物のプログラムとして差し込み直す。
add_action( 'wp_footer', function () {
	if ( is_admin() || ! ishinazaka_chatbot_is_allowed_page() ) {
		return;
	}
	// 二重に読み込まれてもローダーは1回だけ出す（コピーごとに別関数になるためグローバルで共有する）。
	if ( ! empty( $GLOBALS['ishinazaka_chatbot_loader_printed'] ) ) {
		return;
	}
	$GLOBALS['ishinazaka_chatbot_loader_printed'] = true;
	$delay = (int) ISHINAZAKA_CHATBOT_DELAY_MS;
	?>
<script data-noptimize="1">
(function () {
	var loaded = false;
	var events = ['mousemove', 'touchstart', 'keydown', 'scroll', 'click'];
	function load() {
		if (loaded) { return; }
		loaded = true;
		var placeholders = document.querySelectorAll('script[data-ishinazaka-delay-src]');
		Array.prototype.forEach.call(placeholders, function (old) {
			var s = document.createElement('script');
			s.src = old.getAttribute('data-ishinazaka-delay-src');
			if (old.id) { s.id = old.id; }
			old.parentNode.insertBefore(s, old);
			old.parentNode.removeChild(old);
		});
	}
	events.forEach(function (ev) { window.addEventListener(ev, load, { passive: true, once: true }); });
	<?php if ( $delay > 0 ) : ?>
	window.setTimeout(load, <?php echo $delay; ?>);
	<?php endif; ?>
})();
</script>
	<?php
}, 999 );
