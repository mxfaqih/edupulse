<?php
require_once 'db.php';

function isLoggedIn() {
    return isset($_SESSION['user_id']);
}

function getCurrentUserId() {
    return $_SESSION['user_id'] ?? null;
}

function isTeacher() {
    if (!isLoggedIn()) return false;
    $userId = getCurrentUserId();
    $result = dbQuery("SELECT role FROM Users WHERE user_id = ?", [$userId]);
    $user = mysqli_fetch_assoc($result);
    return $user && $user['role'] === 'guru';
}

function getUserName($userId) {
    $result = dbQuery("SELECT name FROM Users WHERE user_id = ?", [$userId]);
    $user = mysqli_fetch_assoc($result);
    return $user ? $user['name'] : '';
}

function getAttendanceData($userId, $month, $year) {
    $result = dbQuery("SELECT date, status FROM Attendance WHERE user_id = ? AND MONTH(date) = ? AND YEAR(date) = ?", 
                      [$userId, $month, $year]);
    $attendance = [];
    while ($row = mysqli_fetch_assoc($result)) {
        $attendance[$row['date']] = $row['status'];
    }
    return $attendance;
}

function getLeaderboard($classroomId) {
    $result = dbQuery("SELECT u.name, SUM(ip.points) as total_points 
                       FROM Users u 
                       JOIN InteractionPoints ip ON u.user_id = ip.user_id 
                       JOIN ClassRoomStudents crs ON u.user_id = crs.student_id 
                       WHERE crs.classroom_id = ? 
                       GROUP BY u.user_id 
                       ORDER BY total_points DESC 
                       LIMIT 10", [$classroomId]);
    $leaderboard = [];
    while ($row = mysqli_fetch_assoc($result)) {
        $leaderboard[] = $row;
    }
    return $leaderboard;
}

function getLightingSettings($classroomId) {
    $result = dbQuery("SELECT mode, brightness_level FROM LightingSettings WHERE classroom_id = ?", [$classroomId]);
    return mysqli_fetch_assoc($result);
}

function getPoseDetectionSettings($classroomId) {
    $result = dbQuery("SELECT is_active, interval FROM PoseDetectionSettings WHERE classroom_id = ?", [$classroomId]);
    return mysqli_fetch_assoc($result);
}

function sanitizeInput($input) {
    return htmlspecialchars(trim($input), ENT_QUOTES, 'UTF-8');
}

function redirectTo($path) {
    header("Location: " . SITE_URL . $path);
    exit();
}

// Tambahkan fungsi-fungsi lain sesuai kebutuhan
