<?php
// index.php
include 'includes/config.php';
include 'includes/db.php';
include 'includes/functions.php';

// Cek apakah user sudah login
$loggedIn = false; // Ganti dengan logika autentikasi sebenarnya
$userName = ''; // Nama user jika sudah login
?>

<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EduPulse - Dashboard</title>
    <link rel="stylesheet" href="public/css/style.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script>
        function checkPostureStatus() {
            $.ajax({
                url: 'posture_status.json',
                type: 'GET',
                dataType: 'json',
                success: function(data) {
                    if (data.status === 'slouching') {
                        $('#notification').text('Siswa sedang bungkuk! Waktu: ' + data.timestamp).show();
                        document.getElementById('alert-sound').play();
                    } else {
                        $('#notification').hide();
                    }
                },
                
            });
        }
    
        $(document).ready(function() {
            checkPostureStatus(); // Periksa status pertama kali
            setInterval(checkPostureStatus, 2000); // Periksa status setiap 2 detik
        });
    </script>
</head>
<body>
    <nav class="navbar">
        <div class="logo">EduPulse</div>
        <div class="nav-right">
            <?php if ($loggedIn): ?>
                <span class="user-name"><?php echo htmlspecialchars($userName); ?></span>
            <?php else: ?>
                <a href="pages/login.php" class="btn">Login</a>
                <a href="pages/register.php" class="btn">Sign Up</a>
            <?php endif; ?>
        </div>
    </nav>

    <main class="dashboard">
        <h1>Selamat Datang di EduPulse</h1>
        
        <section class="attendance-calendar">
            <h2>Kalender Absensi</h2>
            <!-- Implementasi kalender absensi di sini -->
        </section>

        <section class="leaderboard">
            <h2>Leaderboard Keaktifan</h2>
            <!-- Implementasi leaderboard di sini -->
        </section>

        <?php if (isTeacher()): // Fungsi untuk cek apakah user adalah guru ?>
        <section class="classroom-controls">
            <h2>Kontrol Ruang Kelas</h2>
            <div class="lighting-control">
                <h3>Pengaturan Pencahayaan</h3>
                <!-- Kontrol pencahayaan di sini -->
            </div>
            <div class="pose-detection">
                <h3>Deteksi Postur</h3>
                <div id="notification" class="notification" style="display: none;"></div>
                <audio id="alert-sound" src="new-notification-7-210334.mp3" preload="auto"></audio> <!-- Tambahkan file suara di sini -->
            </div>
        </section>
        <?php endif; ?>
    </main>

    <script src="public/js/script.js"></script>
</body>
</html>
