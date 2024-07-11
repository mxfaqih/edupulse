<?php
require_once 'config.php';

function getDbConnection() {
    static $conn;
    if ($conn === null) {
        $conn = mysqli_connect(DB_HOST, DB_USER, DB_PASS, DB_NAME);
        if (!$conn) {
            die("Koneksi database gagal: " . mysqli_connect_error());
        }
        mysqli_set_charset($conn, "utf8mb4");
    }
    return $conn;
}

function dbQuery($sql, $params = []) {
    $conn = getDbConnection();
    $stmt = mysqli_prepare($conn, $sql);
    
    if ($stmt === false) {
        die("Error pada prepared statement: " . mysqli_error($conn));
    }
    
    if (!empty($params)) {
        $types = str_repeat('s', count($params));
        mysqli_stmt_bind_param($stmt, $types, ...$params);
    }
    
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    
    return $result;
}
