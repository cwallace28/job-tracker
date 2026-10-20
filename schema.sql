CREATE TABLE IF NOT EXISTS companies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    website TEXT,
    notes TEXT
);


CREATE TABLE IF NOT EXISTS applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE RESTRICT,
    title VARCHAR(255) NOT NULL,
    job_url TEXT,
    source VARCHAR(255) NOT NULL,
    applied_on DATE NOT NULL,
    current_status ENUM('applied', 'screen', 'interview', 'offer', 'accepted', 'rejected', 'withdrawn') DEFAULT 'applied' NOT NULL,
    follow_up_on DATE,
    INDEX idx_current_status (current_status),
    INDEX idx_follow_up_on (follow_up_on)
);

CREATE TABLE IF NOT EXISTS contacts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS status_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT NOT NULL,
    status ENUM('applied', 'screen', 'interview', 'offer', 'accepted', 'rejected', 'withdrawn') NOT NULL,
    changed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    INDEX idx_application_changed (application_id, changed_at)
);