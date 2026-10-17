<?php
// Unit test for server/lt-stats.php with minimal WordPress stand-ins. Run: php level-test/tools/test_lt_stats.php
define( 'ABSPATH', '/' );
define( 'HOUR_IN_SECONDS', 3600 );
define( 'DAY_IN_SECONDS', 86400 );

$GLOBALS['actions'] = array(); $GLOBALS['routes'] = array(); $GLOBALS['types'] = array();
$GLOBALS['transients'] = array(); $GLOBALS['posts'] = array(); $GLOBALS['meta'] = array(); $GLOBALS['admin'] = false;
function add_action( $h, $f ) { $GLOBALS['actions'][ $h ][] = $f; }
function do_action( $h ) { foreach ( $GLOBALS['actions'][ $h ] ?? array() as $f ) { $f(); } }
function register_post_type( $t, $a ) { $GLOBALS['types'][ $t ] = $a; }
function register_rest_route( $ns, $r, $a ) { $GLOBALS['routes'][ $ns . $r ] = $a; }
function current_user_can( $c ) { return $GLOBALS['admin']; }
function get_transient( $k ) { return $GLOBALS['transients'][ $k ] ?? false; }
function set_transient( $k, $v, $t ) { $GLOBALS['transients'][ $k ] = $v; return true; }
function sanitize_text_field( $s ) { return trim( (string) $s ); }
function wp_unslash( $s ) { return $s; }
function wp_salt( $s ) { return 'salt'; }
function absint( $v ) { return abs( (int) $v ); }
function is_wp_error( $v ) { return false; }
function wp_insert_post( $p, $e ) { $id = count( $GLOBALS['posts'] ) + 100; $p['post_date'] = '2026-10-17 12:00:00'; $GLOBALS['posts'][ $id ] = $p; return $id; }
function update_post_meta( $id, $k, $v ) { $GLOBALS['meta'][ $id ][ $k ] = $v; }
function get_post_meta( $id, $k, $s ) { return $GLOBALS['meta'][ $id ][ $k ] ?? ''; }
function get_post_field( $f, $id ) { return $GLOBALS['posts'][ $id ][ $f ] ?? ''; }
function get_posts( $q ) { return array_keys( array_filter( $GLOBALS['posts'], fn( $p ) => $p['post_type'] === $q['post_type'] ) ); }
class WP_REST_Response { public $data; public $status; function __construct( $d, $s ) { $this->data = $d; $this->status = $s; } }
class Req { private $p; function __construct( $p ) { $this->p = $p; } function get_param( $k ) { return $this->p[ $k ] ?? null; } }

$src = file_get_contents( __DIR__ . '/../server/lt-stats.php' );
foreach ( array( '<', '>', '&', '\\' ) as $bad ) {
	if ( false !== strpos( $src, $bad ) ) { echo "FAIL snippet contains '$bad' (the installer filters it)\n"; exit( 1 ); }
}
eval( $src );
do_action( 'init' ); do_action( 'rest_api_init' );

$fail = 0;
function check( $c, $m ) { global $fail; echo ( $c ? 'ok   ' : 'FAIL ' ) . $m . "\n"; if ( ! $c ) { $fail++; } }
function post( $body ) { $r = $GLOBALS['routes']['bai/v1/lt-stat']; return call_user_func( $r['callback'], new Req( $body ) ); }

$code = '120261017' . str_repeat( '3', 21 ) . str_repeat( '4', 19 );
check( isset( $GLOBALS['types']['bai_lt_stat'] ) && false === $GLOBALS['types']['bai_lt_stat']['public'], 'record type registered, not public' );
check( '__return_true' === $GLOBALS['routes']['bai/v1/lt-stat']['permission_callback'], 'POST /lt-stat is public' );
$r = post( array( 'code' => $code, 'd' => 734, 'e' => 0 ) );
check( 200 === $r->status && true === $r->data['ok'], 'valid attempt saved' );
$id = array_key_last( $GLOBALS['posts'] );
check( $code === $GLOBALS['posts'][ $id ]['post_content'], 'answer code stored as content' );
check( 'private' === $GLOBALS['posts'][ $id ]['post_status'], 'record is private' );
check( 734 === $GLOBALS['meta'][ $id ]['_bai_lts_d'] && 0 === $GLOBALS['meta'][ $id ]['_bai_lts_e'], 'duration and early flag stored' );
$stored = json_encode( array( $GLOBALS['posts'], $GLOBALS['meta'] ) );
$_SERVER['REMOTE_ADDR'] = '203.0.113.7';
post( array( 'code' => $code, 'd' => 999999, 'e' => 1 ) );
$id2 = array_key_last( $GLOBALS['posts'] );
check( 86400 === $GLOBALS['meta'][ $id2 ]['_bai_lts_d'] && 1 === $GLOBALS['meta'][ $id2 ]['_bai_lts_e'], 'duration capped at one day, early flag 1' );
check( false === strpos( json_encode( array( $GLOBALS['posts'], $GLOBALS['meta'] ) ), '203.0.113.7' ), 'IP address is not stored with any record' );
foreach ( array( '', 'abc', '1202610173', $code . '1', $code . "\n", str_replace( '3', '5', $code ), '<script>' ) as $bad ) {
	check( 400 === post( array( 'code' => $bad ) )->status, 'rejected invalid code ' . json_encode( substr( $bad, 0, 14 ) ) );
}
// per-visitor limit: 20 per hour (2 used above by this visitor key? the first had no REMOTE_ADDR, so a different key)
$_SERVER['REMOTE_ADDR'] = '198.51.100.9';
$codes = array();
for ( $i = 0; $i < 25; $i++ ) { $codes[] = post( array( 'code' => $code ) )->status; }
check( 20 === count( array_filter( $codes, fn( $s ) => 200 === $s ) ) && 429 === $codes[20], 'visitor limited to 20 per hour, then 429' );
$_SERVER['REMOTE_ADDR'] = '198.51.100.10';
check( 200 === post( array( 'code' => $code ) )->status, 'another visitor is not affected by that limit' );
// daily cap
$GLOBALS['transients'][ 'bai_lts_day_' . gmdate( 'Ymd' ) ] = 2000;
$_SERVER['REMOTE_ADDR'] = '198.51.100.11';
check( 429 === post( array( 'code' => $code ) )->status, 'site-wide cap of 2000 per day' );
// export
$ex = $GLOBALS['routes']['bai/v1/lt-stats'];
check( false === call_user_func( $ex['permission_callback'] ), 'export refused for non-admins' );
$GLOBALS['admin'] = true;
check( true === call_user_func( $ex['permission_callback'] ), 'export allowed for administrators' );
$rows = call_user_func( $ex['callback'], new Req( array() ) )->data;
check( count( $rows ) === count( $GLOBALS['posts'] ) && array( 'at', 'code', 'd', 'e' ) === array_keys( $rows[0] ), 'export returns every record with at/code/d/e only' );
echo $fail ? "\n$fail FAILED\n" : "\nall checks passed\n";
exit( $fail ? 1 : 0 );
