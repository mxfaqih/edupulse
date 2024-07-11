-- Membuat database
CREATE DATABASE edupulse_master;

-- Menggunakan database
USE edupulse_master;

-- Tabel Users
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    student_number VARCHAR(20),
    role ENUM('guru', 'siswa') NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabel FaceData
CREATE TABLE FaceData (
    face_data_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    face_encoding BLOB NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Tabel Attendance
CREATE TABLE Attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    date DATE NOT NULL,
    status ENUM('hadir', 'tidak hadir') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Tabel InteractionPoints
CREATE TABLE InteractionPoints (
    interaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    points INT NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Tabel ClassRooms
CREATE TABLE ClassRooms (
    classroom_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    teacher_id INT,
    FOREIGN KEY (teacher_id) REFERENCES Users(user_id)
);

-- Tabel ClassRoomStudents
CREATE TABLE ClassRoomStudents (
    classroom_student_id INT AUTO_INCREMENT PRIMARY KEY,
    classroom_id INT,
    student_id INT,
    FOREIGN KEY (classroom_id) REFERENCES ClassRooms(classroom_id),
    FOREIGN KEY (student_id) REFERENCES Users(user_id)
);

-- Tabel PoseDetectionLogs
CREATE TABLE PoseDetectionLogs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    posture_status ENUM('baik', 'buruk') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Tabel LightingSettings
CREATE TABLE LightingSettings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    classroom_id INT,
    mode ENUM('otomatis', 'manual') NOT NULL,
    brightness_level INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (classroom_id) REFERENCES ClassRooms(classroom_id)
);

-- Tabel PoseDetectionSettings
CREATE TABLE PoseDetectionSettings (
    setting_id INT AUTO_INCREMENT PRIMARY KEY,
    classroom_id INT,
    is_active BOOLEAN NOT NULL,
    interval INT NOT NULL,
    FOREIGN KEY (classroom_id) REFERENCES ClassRooms(classroom_id)
);