/**
 * BAI - Görüşme hatırlatması: tek seferlik, 1 saat önce (stopgap)
 *
 * The bai-booking plugin (v0.8.0) sends the interview reminder on every run of its hourly job
 * once the interview is less than 24 hours away, never records that it was sent, and titles the
 * owner copy "Yarın görüşme" even on the day itself. Mahdiyeh's 15 Oct 22:00 interview produced
 * 8 reminders each for her and for the owner on live.
 *
 * Until the plugin is fixed, this snippet works on the reminder emails only:
 * 1. Holds them until the interview is at most 75 minutes away (date and time are read from the
 *    subject, Turkey time). Because the plugin retries every hour, the first run inside that window
 *    delivers the reminder about an hour before.
 * 2. Lets each one through once per recipient per interview time. A rescheduled interview has a new
 *    time in its subject, so it gets its own single reminder.
 * 3. Renames the owner subject "Yarın görüşme:" to "Görüşme hatırlatması:" (the date stays).
 * If the date cannot be read, the reminder is still sent once. All other emails are untouched.
 *
 * Remove it once the booking plugin itself sends a single 1-hour-before reminder.
 *
 * Install: Code Snippets → + Add Snippet → Add Your Custom Code → PHP Snippet,
 * paste this whole file, Insert Method: Auto Insert, Location: Run Everywhere, activate.
 */

if ( ! function_exists( 'bai_iv_reminder_start' ) ) {
	/**
	 * Interview start (Unix time) read from a reminder subject, or 0 when it cannot be read.
	 * Handles "Thursday 15 October, 22:00" and "15 Ekim Perşembe, 22:00".
	 *
	 * @param string $subject Mail subject.
	 * @param int    $now     Current Unix time.
	 * @return int
	 */
	function bai_iv_reminder_start( $subject, $now ) {
		$months = array(
			'january' => 1, 'february' => 2, 'march' => 3, 'april' => 4, 'may' => 5, 'june' => 6,
			'july' => 7, 'august' => 8, 'september' => 9, 'october' => 10, 'november' => 11, 'december' => 12,
			'ocak' => 1, 'şubat' => 2, 'mart' => 3, 'nisan' => 4, 'mayıs' => 5, 'haziran' => 6,
			'temmuz' => 7, 'ağustos' => 8, 'eylül' => 9, 'ekim' => 10, 'kasım' => 11, 'aralık' => 12,
		);
		if ( ! preg_match( '/(\d{1,2})\s+(\p{L}+)\D*?(\d{1,2}):(\d{2})/u', $subject, $m ) ) {
			return 0;
		}
		$name = mb_strtolower( $m[2], 'UTF-8' );
		if ( ! isset( $months[ $name ] ) ) {
			return 0;
		}
		$tz   = function_exists( 'wp_timezone' ) ? wp_timezone() : new DateTimeZone( 'Europe/Istanbul' );
		$year = (int) ( new DateTime( '@' . $now ) )->setTimezone( $tz )->format( 'Y' );
		foreach ( array( $year, $year + 1 ) as $y ) {
			$d = DateTime::createFromFormat( 'Y-n-j G:i', $y . '-' . $months[ $name ] . '-' . (int) $m[1] . ' ' . (int) $m[3] . ':' . $m[4], $tz );
			if ( $d ) {
				$t = $d->getTimestamp();
				if ( $t > $now - 180 * DAY_IN_SECONDS ) {
					return $t;
				}
			}
		}
		return 0;
	}

	/**
	 * What to do with an outgoing email: 'other', 'send' or 'block'. Records each reminder it lets through.
	 *
	 * @param string $to      Recipient list, comma separated.
	 * @param string $subject Mail subject.
	 * @param int    $now     Current Unix time.
	 * @return string
	 */
	function bai_iv_reminder_decide( $to, $subject, $now ) {
		$is_reminder = ( 0 === stripos( $subject, 'Reminder: your interview' ) )
			|| ( 0 === strpos( $subject, 'Yarın görüşme:' ) )
			|| ( 0 === strpos( $subject, 'Hatırlatma: görüşme' ) );
		if ( ! $is_reminder ) {
			return 'other';
		}
		$start = bai_iv_reminder_start( $subject, $now );
		if ( $start ) {
			if ( $start - $now > 75 * MINUTE_IN_SECONDS ) {
				return 'block'; // Too early: the plugin tries again next hour.
			}
			if ( $now > $start ) {
				return 'block'; // Interview already started.
			}
		}
		$key = 'bai_iv_rem_' . md5( strtolower( trim( $to ) ) . '|' . $subject );
		if ( get_transient( $key ) ) {
			return 'block';
		}
		set_transient( $key, $now, 3 * DAY_IN_SECONDS );
		return 'send';
	}
}

add_filter(
	'wp_mail',
	function ( $atts ) {
		$to      = is_array( $atts['to'] ) ? implode( ',', $atts['to'] ) : (string) $atts['to'];
		$subject = (string) $atts['subject'];
		$verdict = bai_iv_reminder_decide( $to, $subject, time() );
		if ( 'block' === $verdict ) {
			$atts['to']           = array();
			$atts['bai_iv_block'] = 1;
		} elseif ( 'send' === $verdict ) {
			$atts['subject'] = preg_replace( '/^Yarın görüşme:/u', 'Görüşme hatırlatması:', $subject );
		}
		return $atts;
	},
	1
);

add_filter(
	'pre_wp_mail',
	function ( $return, $atts ) {
		if ( ! empty( $atts['bai_iv_block'] ) ) {
			return false;
		}
		return $return;
	},
	0,
	2
);
