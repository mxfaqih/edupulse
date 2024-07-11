<?php
// Konfigurasi dasar
define('DB_HOST', 'localhost');
define('DB_USER', 'root');
define('DB_PASS', '');
define('DB_NAME', 'edupulse_master');

// Zona waktu
date_default_timezone_set('Asia/Jakarta');

// Konfigurasi sesi
ini_set('session.cookie_lifetime', 60 * 60 * 24 * 7);  // 1 minggu
ini_set('session.gc_maxlifetime', 60 * 60 * 24 * 7);  // 1 minggu
session_start();

// Konstanta lain yang mungkin diperlukan
define('SITE_URL', 'http://localhost/edupulse');
