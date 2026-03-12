import sqlite3
import os
import re

class LeadDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    normalized_phone TEXT,
                    website TEXT,
                    address TEXT,
                    emails TEXT,
                    socials TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, normalized_phone, address)
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_name ON leads(name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_phone ON leads(normalized_phone)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_address ON leads(address)')

    def normalize_phone(self, phone):
        if not phone:
            return ""
        return re.sub(r'[^0-9]', '', str(phone))

    def is_duplicate(self, name, phone, address=""):
        name_clean = str(name).lower().strip()
        phone_clean = self.normalize_phone(phone)
        addr_clean = str(address).lower().strip()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. Match by name AND phone (Best match)
            if phone_clean:
                cursor.execute('''
                    SELECT 1 FROM leads 
                    WHERE LOWER(name) = ? AND normalized_phone = ? 
                    LIMIT 1
                ''', (name_clean, phone_clean))
                if cursor.fetchone():
                    return True
            
            # 2. Match by name AND address (Fallback match)
            if addr_clean:
                cursor.execute('''
                    SELECT 1 FROM leads 
                    WHERE LOWER(name) = ? AND LOWER(address) = ? 
                    LIMIT 1
                ''', (name_clean, addr_clean))
                if cursor.fetchone():
                    return True
                    
        return False

    def add_leads(self, leads):
        """Leads is a list of dicts with 'name', 'phone', 'website', 'address'"""
        added_count = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for lead in leads:
                name = lead.get('name', '')
                phone = lead.get('phone', '')
                website = lead.get('website', '')
                address = lead.get('address', '')
                emails = lead.get('emails', '')
                if isinstance(emails, list):
                    emails = "; ".join(emails)
                socials = lead.get('socials', '')
                norm_phone = self.normalize_phone(phone)
                
                try:
                    cursor.execute('''
                        INSERT INTO leads (name, phone, normalized_phone, website, address, emails, socials)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (name, phone, norm_phone, website, address, emails, socials))
                    added_count += 1
                except sqlite3.IntegrityError:
                    # Update existing lead with new data if available (merging)
                    cursor.execute('''
                        UPDATE leads SET 
                            website = COALESCE(NULLIF(?, ''), website),
                            emails = COALESCE(NULLIF(?, ''), emails),
                            socials = COALESCE(NULLIF(?, ''), socials)
                        WHERE LOWER(name) = ? AND (normalized_phone = ? OR LOWER(address) = ?)
                    ''', (website, emails, socials, name.lower().strip(), norm_phone, address.lower().strip()))
                    continue
            conn.commit()
        return added_count

    def get_stats(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM leads')
            return {"total_leads": cursor.fetchone()[0]}
