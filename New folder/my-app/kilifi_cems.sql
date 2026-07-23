-- 1. Sub-Counties & Field Stations Table
CREATE TABLE sub_counties (
    sub_county_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE, -- e.g., 'Kilifi North', 'Malindi', 'Magarini', 'Ganze', 'Rabai', 'Kaloleni', 'Kilifi South'
    headquarters_location VARCHAR(100) NOT NULL
);

-- 2. Departments Table
CREATE TABLE departments (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(100) NOT NULL UNIQUE, -- e.g., 'Health & Sanitation', 'Agriculture', 'Finance'
    code VARCHAR(10) NOT NULL UNIQUE
);

-- 3. Officers / Employees Table
CREATE TABLE officers (
    officer_id INT PRIMARY KEY AUTO_INCREMENT,
    pf_number VARCHAR(20) NOT NULL UNIQUE, -- Personal File / Payroll Number (e.g., PF-88021)
    national_id VARCHAR(20) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    dept_id INT NOT NULL,
    sub_county_id INT NOT NULL,
    job_group VARCHAR(5) NOT NULL, -- e.g., 'Group K', 'Group N'
    role ENUM('officer', 'supervisor', 'director', 'cpsb_admin') DEFAULT 'officer',
    current_status ENUM('on_duty', 'on_leave', 'sick_off', 'off_duty', 'absent') DEFAULT 'off_duty',
    annual_leave_balance INT DEFAULT 21, -- Statutory starting balance (Sec 28)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id),
    FOREIGN KEY (sub_county_id) REFERENCES sub_counties(sub_county_id)
);

-- 4. Statutory Leave Applications Table
CREATE TABLE leave_applications (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    officer_id INT NOT NULL,
    leave_type ENUM('annual', 'maternity', 'paternity', 'sick') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_requested INT NOT NULL,
    medical_cert_url VARCHAR(255) NULL, -- Required for sick leave > 1 day (Sec 30)
    status ENUM('pending_supervisor', 'pending_director', 'approved', 'rejected') DEFAULT 'pending_supervisor',
    rejection_reason TEXT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (officer_id) REFERENCES officers(officer_id)
);

-- 5. Real-Time Duty & Check-In Logs
CREATE TABLE duty_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    officer_id INT NOT NULL,
    check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_out_time TIMESTAMP NULL,
    work_station_location VARCHAR(100) NOT NULL,
    verification_method ENUM('biometric', 'portal_checkin', 'supervisor_override') DEFAULT 'portal_checkin',
    FOREIGN KEY (officer_id) REFERENCES officers(officer_id)
);

-- 6. CPSB Audit Trail Table (Immutable System Log)
CREATE TABLE audit_logs (
    audit_id INT PRIMARY KEY AUTO_INCREMENT,
    actor_officer_id INT NOT NULL, -- Who performed the action
    action_performed VARCHAR(255) NOT NULL, -- e.g., "Approved Annual Leave for PF-88021"
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (actor_officer_id) REFERENCES officers(officer_id)
);