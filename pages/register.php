<?php
require_once '../includes/config.php';
require_once '../includes/db.php';
require_once '../includes/functions.php';

$error = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $name = sanitizeInput($_POST['name']);
    $email = sanitizeInput($_POST['email']);
    $password = $_POST['password'];
    $confirm_password = $_POST['confirm_password'];
    $role = sanitizeInput($_POST['role']);
    $student_number = $role == 'siswa' ? sanitizeInput($_POST['student_number']) : null;

    if ($password !== $confirm_password) {
        $error = "Password tidak cocok.";
    } else {
        $result = dbQuery("SELECT user_id FROM Users WHERE email = ?", [$email]);
        if (mysqli_num_rows($result) > 0) {
            $error = "Email sudah terdaftar.";
        } else {
            $password_hash = password_hash($password, PASSWORD_DEFAULT);
            $query = "INSERT INTO Users (name, email, password_hash, role, student_number) VALUES (?, ?, ?, ?, ?)";
            $result = dbQuery($query, [$name, $email, $password_hash, $role, $student_number]);

            if ($result) {
                redirectTo('/pages/login.php');
            } else {
                $error = "Gagal mendaftar. Silakan coba lagi.";
            }
        }
    }
}
?>

<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrasi - EduPulse</title>
    <link rel="stylesheet" href="../public/css/style.css">
</head>
<body>
    <div class="register-container">
        <h2>Registrasi EduPulse</h2>
        <?php if ($error): ?>
            <p class="error"><?php echo $error; ?></p>
        <?php endif; ?>
        <form method="POST" action="">
            <div class="form-group">
                <label for="name">Nama:</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="form-group">
                <label for="confirm_password">Konfirmasi Password:</label>
                <input type="password" id="confirm_password" name="confirm_password" required>
            </div>
            <div class="form-group">
                <label for="role">Peran:</label>
                <select id="role" name="role" required>
                    <option value="siswa">Siswa</option>
                    <option value="guru">Guru</option>
                </select>
            </div>
            <div class="form-group" id="student_number_group" style="display:none;">
                <label for="student_number">Nomor Induk Siswa:</label>
                <input type="text" id="student_number" name="student_number">
            </div>
            <button type="submit" class="btn">Daftar</button>
        </form>
        <p>Sudah punya akun? <a href="login.php">Login disini</a></p>
    </div>

    <script>
        document.getElementById('role').addEventListener('change', function() {
            var studentNumberGroup = document.getElementById('student_number_group');
            if (this.value === 'siswa') {
                studentNumberGroup.style.display = 'block';
            } else {
                studentNumberGroup.style.display = 'none';
            }
        });
    </script>
</body>
</html>
