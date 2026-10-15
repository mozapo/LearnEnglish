<?php
const DAY_IN_SECONDS = 86400; $T = array(); $F = array();
function get_transient($k){ global $T; return $T[$k] ?? false; }
function set_transient($k,$v,$e){ global $T; $T[$k]=$v; }
function add_filter($h,$cb,$p=10,$n=1){ global $F; $F[$h][]=array($cb,$n); }
eval( file_get_contents( $argv[1] ?? __DIR__ . "/../bai-interview-reminder-once.php" ) );
function send($to,$subj){ global $F; $a=array('to'=>$to,'subject'=>$subj,'message'=>'');
  foreach($F['wp_mail'] as $f) $a=$f[0]($a); $r=null; foreach($F['pre_wp_mail'] as $f) $r=$f[0]($r,$a);
  return ($r===false) ? 'BLOCKED' : 'sent'; }
$c='mahdiyehbadiee@gmail.com'; $o='mohammad.zamanipour@gmail.com';
$cases=array(
 array($c,'Reminder: your interview Thursday 15 October, 22:00','sent'),
 array($o,'Yarın görüşme: Mahdiyeh Badiee — 15 Ekim Perşembe, 22:00','sent'),
 array($c,'Reminder: your interview Thursday 15 October, 22:00','BLOCKED'),
 array($o,'Yarın görüşme: Mahdiyeh Badiee — 15 Ekim Perşembe, 22:00','BLOCKED'),
 array($c,'Reminder: your interview Friday 16 October, 18:00','sent'),
 array($c,'Interview booked: Thursday 15 October, 22:00','sent'),
 array($c,'Interview booked: Thursday 15 October, 22:00','sent'),
 array('x@y.com','Hatırlatma: sözleşme paketin · Reminder: your agreement packet','sent'),
 array('x@y.com','Hatırlatma: sözleşme paketin · Reminder: your agreement packet','sent'),
);
$fail=0; foreach($cases as $i=>$k){ $g=send($k[0],$k[1]); if($g!==$k[2]){$fail++;} echo ($g===$k[2]?'ok  ':'FAIL')." #$i $g  {$k[1]}\n"; }
exit($fail?1:0);
