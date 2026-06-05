import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "township.db")

_conn = None


def get_connection():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
    return _conn


def migrate_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(affairs)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'department_id' not in columns:
            cursor.execute("ALTER TABLE affairs ADD COLUMN department_id INTEGER REFERENCES departments(id)")
            conn.commit()
    except:
        pass


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            id_card TEXT NOT NULL UNIQUE,
            gender TEXT NOT NULL CHECK(gender IN ('男', '女')),
            birth_date TEXT NOT NULL,
            phone TEXT,
            address TEXT NOT NULL,
            village TEXT NOT NULL,
            household_head TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS affairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('户籍', '社保', '医保', '低保', '建房', '计生', '其他')),
            applicant_id INTEGER NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT '待受理' CHECK(status IN ('待受理', '办理中', '已办结', '已退回')),
            department_id INTEGER,
            handler TEXT,
            result TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (applicant_id) REFERENCES residents(id),
            FOREIGN KEY (department_id) REFERENCES departments(id)
        );

        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('通知', '公告', '政策', '公示')),
            publisher TEXT NOT NULL,
            is_pinned INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            manager TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        );

        CREATE TABLE IF NOT EXISTS petitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('投诉举报', '意见建议', '求助咨询', '信息公开申请')),
            target TEXT NOT NULL,
            content TEXT NOT NULL,
            demand TEXT,
            contact TEXT,
            is_anonymous INTEGER DEFAULT 0,
            status TEXT NOT NULL DEFAULT '待签收' CHECK(status IN (
                '待签收', '待分派', '办理中', '待审核', '已办结', '退回重办', '复查中', '复查完结'
            )),
            department_id INTEGER,
            deadline TEXT,
            process_result TEXT,
            review_opinion TEXT,
            review_result TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (department_id) REFERENCES departments(id)
        );

        CREATE TABLE IF NOT EXISTS petition_urges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            petition_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            operator TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (petition_id) REFERENCES petitions(id)
        );

        CREATE TABLE IF NOT EXISTS petition_flow_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            petition_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            operator TEXT,
            remark TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (petition_id) REFERENCES petitions(id)
        );
    """)

    conn.commit()
