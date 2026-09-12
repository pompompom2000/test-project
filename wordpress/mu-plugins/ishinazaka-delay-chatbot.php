<?php
/**
 * Plugin Name: 石名坂 チャットボット遅延読込
 * Description: AI Engine のチャットボット本体スクリプト（約320KB）を、訪問者が最初に操作したとき、または一定秒数後まで読み込まないようにします。
 * Version:     1.0.0
 *
 * 設置場所: wp-content/mu-plugins/ （このサイトでは /common/files/mu-plugins/ 相当）
 *           mu-plugins は有効化操作が不要で、ファイルを置くだけで動きます。
 *
 * 動作:
 *   1. AI Engine が出力する <script id="mwai_chatbot-js" src="..."> を
 *      type="text/plain" に書き換え、ブラウザが実行しないようにする。
 *   2. フッターに小さなローダーを出し、次のどちらか早い方で本物のスクリプトを差し込む。
 *        - マウス移動 / タッチ / キー入力 / スクロール / クリック のいずれか
 *        - ページ表示から ISHINAZAKA_CHATBOT_DELAY_MS ミリ秒経過（初期値 8 秒）
 *   3. ISHINAZAKA_CHATBOT_ONLY_PATHS に配列を入れると、そのパスで始まるページ以外では
 *      チャットボットのスクリプトとCSSを読み込まない（完全に外す）。
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// 何もしなくても表示されるまでの待ち時間（ミリ秒）。0 にすると操作があるまで読み込まない。
if ( ! defined( 'ISHINAZAKA_CHATBOT_DELAY_MS' ) ) {
	define( 'ISHINAZAKA_CHATBOT_DELAY_MS', 8000 );
}

// チャットボットを出すページを限定したい場合に使う。空配列なら全ページで（遅延して）読み込む。
// 例: array( '/', '/saiseki-hanbai/', '/simulation/', '/faq/', '/contact/' )
if ( ! defined( 'ISHINAZAKA_CHATBOT_ONLY_PATHS' ) ) {
	define( 'ISHINAZAKA_CHATBOT_ONLY_PATHS', array() );
}

/**
 * 現在のリクエストがチャットボットを出す対象ページかどうか。
 */
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

/**
 * 対象外ページでは AI Engine のスクリプトとCSSをそもそも読み込まない。
 */
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

/**
 * 対象ページでは <script> を実行されない形に書き換える。
 * data-noptimize は Autoptimize に「このタグは触らない」と伝える属性。
 */
add_filter( 'script_loader_tag', function ( $tag, $handle, $src ) {
	if ( 'mwai_chatbot' !== $handle || is_admin() ) {
		return $tag;
	}
	$tag = preg_replace( '/<script\b([^>]*)\bsrc=/', '<script$1data-noptimize="1" type="text/plain" data-ishinazaka-delay-src=', $tag, 1 );
	return $tag;
}, 20, 3 );

/**
 * 差し込み用ローダー。依存する wp-element 等は AI Engine が通常どおり先に読み込んでいる。
 */
add_action( 'wp_footer', function () {
	if ( is_admin() || ! ishinazaka_chatbot_is_allowed_page() ) {
		return;
	}
	$delay = (int) ISHINAZAKA_CHATBOT_DELAY_MS;
	?>
<script data-noptimize="1">
(function () {
	var loaded = false;
	var events = ['mousemove', 'touchstart', 'keydown', 'scroll', 'click'];
	function load() {
		if (loaded) { return; }
		loaded = true;
		events.forEach(function (ev) { window.removeEventListener(ev, load, { passive: true }); });
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
