<?php
// Offline test for bai-job-application-once-a-year.php with minimal WordPress stubs.
// Run: php wpcode/test/run.php
define( 'ABSPATH', '/' );
$GLOBALS['filters'] = array();
function add_filter( $h, $cb ) { $GLOBALS['filters'][ $h ] = $cb; }
function is_email( $e ) { return (bool) filter_var( $e, FILTER_VALIDATE_EMAIL ); }
function current_time() { return '2026-10-15 12:00:00'; }
function maybe_unserialize( $v ) { return @unserialize( $v ); }
function esc_url( $u ) { return $u; }
function home_url( $p ) { return 'https://example.test' . $p; }
function absint( $v ) { return abs( (int) $v ); }
class WP_REST_Response { function __construct( public $data, public $status ) {} }
class Req { function __construct( public $route, public $p ) {} function get_route() { return $this->route; } function get_params() { return $this->p; } function get_param( $k ) { return $this->p[ $k ] ?? null; } }
class FakeDB {
	public $prefix = 'wp_'; public $last_error = ''; public $rows = array(); public $sql = '';
	function prepare( $q, ...$a ) { return vsprintf( str_replace( '%s', "'%s'", $q ), $a ); }
	function get_var( $q ) { return 'wp_srfm_entries'; }
	function get_col( $q ) { $this->sql = $q; preg_match( "/created_at BETWEEN '([^']+)'/", $q, $m );
		return array_column( array_filter( $this->rows, fn( $r ) => 'trash' !== $r['status'] && $r['created_at'] >= $m[1] ), 'form_data' ); }
}
$wpdb = new FakeDB();
$table_prefix = 'wp_';
require __DIR__ . '/../bai-job-application-once-a-year.php';
$f = $GLOBALS['filters']['rest_pre_dispatch'];

function entry( $email, $phone, $date, $status = 'unread' ) {
	return array( 'status' => $status, 'created_at' => $date, 'form_data' => json_encode( array(
		'srfm-email-eposta-lbl-RS1wb3N0YSBBZHJlc2luaXo' => $email,
		'srfm-number-telefon-lbl-VGVsZWZvbiBOdW1hcmFuxLF6-phone' => $phone ) ) );
}
$wpdb->rows = array(
	entry( 'Ayse@Example.com', '+90 532 111 22 33', '2026-03-01 10:00:00' ),
	entry( 'old@example.com', '0533 999 88 77', '2025-09-01 10:00:00' ),          // older than 365 days
	entry( 'trashed@example.com', '0544 000 00 00', '2026-09-01 10:00:00', 'trash' ),
);
function submit( $form, $email, $phone ) {
	global $f;
	return $f( null, null, new Req( '/sureforms/v1/submit-form', array( 'form-id' => (string) $form,
		'srfm-email-eposta-lbl-RS1wb3N0YSBBZHJlc2luaXo' => $email,
		'srfm-number-telefon-lbl-VGVsZWZvbiBOdW1hcmFuxLF6-phone' => $phone,
		'srfm-sender-email-field' => '', 'srfm-honeypot-field' => '' ) ) );
}
$cases = array(
	array( 'same email, other case/spaces',  3590, '  ayse@EXAMPLE.com ', '0555 123 45 67', true ),
	array( 'same phone, other format',        3590, 'new@example.com', '05321112233', true ),
	array( 'same email on English form',      5609, 'ayse@example.com', '', true ),
	array( 'new person',                      3590, 'new@example.com', '0555 123 45 67', false ),
	array( 'applied 13+ months ago',          3590, 'old@example.com', '0533 999 88 77', false ),
	array( 'trashed entry does not count',    3590, 'trashed@example.com', '0544 000 00 00', false ),
	array( 'other form is untouched',         1234, 'ayse@example.com', '', false ),
);
$fail = 0;
foreach ( $cases as [ $name, $form, $email, $phone, $blocked ] ) {
	$r = submit( $form, $email, $phone );
	$got = $r instanceof WP_REST_Response && 409 === $r->status && false === $r->data['success'];
	printf( "%s  %s\n", $got === $blocked ? 'ok  ' : 'FAIL', $name );
	$fail += $got !== $blocked;
}
$r = $f( null, null, new Req( '/wp/v2/pages', array() ) );
printf( "%s  other routes pass through\n", null === $r ? 'ok  ' : 'FAIL' ); $fail += null !== $r;
$en = submit( 5609, 'ayse@example.com', '' )->data['data']['message'];
printf( "%s  English message on English form\n", str_starts_with( $en, 'We have' ) ? 'ok  ' : 'FAIL' );
// The installer HTML-escapes these characters, so the snippet body must not contain them.
$body = preg_replace( '/^<\?php\s*/', '', file_get_contents( __DIR__ . '/../bai-job-application-once-a-year.php' ) );
$bad  = preg_match( '/[&<>\\\\]/', $body );
printf( "%s  no & < > or backslash in the snippet body\n", $bad ? 'FAIL' : 'ok  ' ); $fail += $bad;
exit( $fail ? 1 : 0 );
