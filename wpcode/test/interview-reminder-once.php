<?php
// Offline test for wpcode/bai-interview-reminder-once.php: php wpcode/test/interview-reminder-once.php
const MINUTE_IN_SECONDS = 60;
const DAY_IN_SECONDS    = 86400;
$T = array();
$F = array();
$NOW = 0;
function get_transient( $k ) { global $T; return $T[ $k ] ?? false; }
function set_transient( $k, $v, $e ) { global $T; $T[ $k ] = $v; }
function add_filter( $h, $cb, $p = 10, $n = 1 ) { global $F; $F[ $h ][] = $cb; }
function wp_timezone() { return new DateTimeZone( 'Europe/Istanbul' ); }
eval( file_get_contents( $argv[1] ?? __DIR__ . '/../bai-interview-reminder-once.php' ) );

// Same pipeline as wp_mail(), but with a fixed clock.
function send( $to, $subj, $at ) {
	global $F;
	$now = ( new DateTime( $at, new DateTimeZone( 'Europe/Istanbul' ) ) )->getTimestamp();
	$v   = bai_iv_reminder_decide( $to, $subj, $now );
	if ( 'block' === $v ) { return 'BLOCKED'; }
	if ( 'send' === $v ) { $subj = preg_replace( '/^Yarın görüşme:/u', 'Görüşme hatırlatması:', $subj ); }
	return 'sent: ' . $subj;
}

$c  = 'mahdiyehbadiee@gmail.com';
$o  = 'mohammad.zamanipour@gmail.com';
$cs = 'Reminder: your interview Thursday 15 October, 22:00';
$os = 'Yarın görüşme: Mahdiyeh Badiee — 15 Ekim Perşembe, 22:00';
$cases = array(
	// Today's real hourly runs on live, interview 15 Oct 22:00.
	array( $c, $cs, '2026-10-14 21:57', 'BLOCKED' ),
	array( $o, $os, '2026-10-14 21:57', 'BLOCKED' ),
	array( $c, $cs, '2026-10-15 13:53', 'BLOCKED' ),
	array( $c, $cs, '2026-10-15 19:52', 'BLOCKED' ),
	array( $c, $cs, '2026-10-15 20:52', 'sent: ' . $cs ),
	array( $o, $os, '2026-10-15 20:52', 'sent: Görüşme hatırlatması: Mahdiyeh Badiee — 15 Ekim Perşembe, 22:00' ),
	array( $c, $cs, '2026-10-15 21:52', 'BLOCKED' ),
	array( $o, $os, '2026-10-15 21:52', 'BLOCKED' ),
	array( $c, $cs, '2026-10-15 22:52', 'BLOCKED' ),
	// Rescheduled to a new time: one new reminder near that time.
	array( $c, 'Reminder: your interview Friday 16 October, 18:00', '2026-10-16 16:30', 'BLOCKED' ),
	array( $c, 'Reminder: your interview Friday 16 October, 18:00', '2026-10-16 17:05', 'sent: Reminder: your interview Friday 16 October, 18:00' ),
	array( $c, 'Reminder: your interview Friday 16 October, 18:00', '2026-10-16 17:40', 'BLOCKED' ),
	// Year boundary: 31 Dec subject read in late December, 2 Jan subject read on 31 Dec.
	array( $c, 'Reminder: your interview Saturday 2 January, 00:30', '2026-12-31 23:50', 'BLOCKED' ),
	array( $c, 'Reminder: your interview Saturday 2 January, 00:30', '2027-01-01 23:40', 'sent: Reminder: your interview Saturday 2 January, 00:30' ),
	// Unreadable date: still sent, once.
	array( $c, 'Reminder: your interview soon', '2026-10-15 12:00', 'sent: Reminder: your interview soon' ),
	array( $c, 'Reminder: your interview soon', '2026-10-15 13:00', 'BLOCKED' ),
	// Other mail is never touched.
	array( $c, 'Interview booked: Thursday 15 October, 22:00', '2026-10-14 20:19', 'sent: Interview booked: Thursday 15 October, 22:00' ),
	array( $c, 'Interview booked: Thursday 15 October, 22:00', '2026-10-14 20:20', 'sent: Interview booked: Thursday 15 October, 22:00' ),
	array( 'x@y.com', 'Hatırlatma: sözleşme paketin · Reminder: your agreement packet', '2026-10-15 10:00', 'sent: Hatırlatma: sözleşme paketin · Reminder: your agreement packet' ),
	array( 'x@y.com', 'Hatırlatma: sözleşme paketin · Reminder: your agreement packet', '2026-10-15 11:00', 'sent: Hatırlatma: sözleşme paketin · Reminder: your agreement packet' ),
);
$fail = 0;
foreach ( $cases as $i => $k ) {
	$got = send( $k[0], $k[1], $k[2] );
	$ok  = $got === $k[3];
	$fail += $ok ? 0 : 1;
	echo ( $ok ? 'ok   ' : 'FAIL ' ) . "#$i {$k[2]}  $got" . ( $ok ? '' : "   (expected {$k[3]})" ) . "\n";
}
echo $fail ? "$fail failed\n" : "all passed\n";
exit( $fail ? 1 : 0 );
