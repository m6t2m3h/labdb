import os
import logging
import sqlite3

from DatabaseDefinition import DatabaseDefinition

class TableDataRepository(DatabaseDefinition):

    def __init__(self):
        self.db_path = self.DATA_BASE_DIR + self.DATA_BASE_NAME + ".db"
        self.logger = logging.getLogger(__name__) 
        os.makedirs(self.DATA_BASE_DIR, exist_ok=True)

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def check_patient(self, patient_data):

        if not patient_data.get("patient_name"):
            return None
        
        sql = f"SELECT * FROM {self.PATIENT_TABLE} WHERE patient_name=?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (patient_data["patient_name"],))
            table_data = cursor.fetchall()

        if not table_data:
            # 新規登録
            column_names = [self.PATIENT_ITEM[column] for column in patient_data.keys()]
            values = list(patient_data.values())
            patient_id = self.insert_patient(column_names, values)
        else:
            #　一致したpatient_id
            patient_id = table_data[0]["patient_id"]
        
        return patient_id

    def output_result(self, id, result):
        column_names = [
            db_name
            for db_name in self.DB_RESULT_ITEM.values()
            if db_name != "result_id"
        ]

        values = [
            int(id) if db_name == "patient_id"
            else result.get(db_name)
            for db_name in self.DB_RESULT_ITEM.values()
            if db_name != "result_id"
        ]

        self.insert_result(column_names, values)

    def create_table(self):

        sql_patient_colmuns =  '''patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            gender TEXT
            '''

        sql_result_colmuns = '''result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            hospital_name TEXT,
            department TEXT,
            doctor TEXT,
            report_date TEXT,
            report_time TEXT,
            reception_date TEXT,
            age INTEGER,
            tp REAL,
            albumin REAL,
            ag_ratio REAL,
            ck REAL,
            ast REAL,
            alt REAL,
            ttt REAL,
            ztt REAL,
            ld_ldh REAL,
            ld_ifcc REAL,
            alp_ifcc REAL,
            alp REAL,
            gamma_gt REAL,
            che REAL,
            lap REAL,
            amylase REAL,
            urine_amylase REAL,
            creatinine REAL,
            egfr REAL,
            ua REAL,
            bun REAL,
            crp REAL,
            grp_srid REAL,
            ammonia REAL,
            blood_glucose REAL,
            hba1c_jds REAL,
            hba1c_ngsp REAL,
            triglyceride REAL,
            total_cholesterol REAL,
            hdl_c REAL,
            ldl_c REAL,
            na REAL,
            k REAL,
            cl REAL,
            ca REAL,
            ip REAL,
            t_bil REAL,
            d_bil REAL,
            i_bil REAL,
            fe REAL,
            tibc REAL,
            tsh REAL,
            ft3 REAL,
            ft4 REAL,
            bnp REAL,
            ck_mb REAL,
            arteriosclerosis_index REAL,
            abo_type TEXT,
            rh_type TEXT,
            influenza_a TEXT,
            influenza_b TEXT,
            h_fabp TEXT,
            pregnancy_test TEXT,
            group_a_strep TEXT,
            tpha_ica TEXT,
            hbs_antigen_ica TEXT,
            hcv_antibody TEXT,
            rpr_card TEXT,
            wbc REAL,
            rbc REAL,
            hemoglobin REAL,
            hematocrit REAL,
            platelet REAL,
            mcv REAL,
            mch REAL,
            mchc REAL,
            differential_count TEXT,
            baso REAL,
            eosino REAL,
            stab REAL,
            seg REAL,
            lympho REAL,
            mono REAL,
            neutro REAL,
            ebl REAL,
            aptt REAL,
            fibrinogen REAL,
            pt REAL,
            pt_time REAL,
            control_value REAL,
            pt_activity REAL,
            pt_inr REAL,
            fdp REAL,
            d_dimer REAL,
            urine_protein TEXT,
            urine_glucose TEXT,
            urine_ph REAL,
            urine_urobilinogen TEXT,
            urine_bilirubin TEXT,
            urine_ketone TEXT,
            urine_occult_blood TEXT,
            urine_sediment TEXT,
            urine_rbc REAL,
            urine_wbc REAL,
            squamous_epithelium TEXT,
            hyaline_cast TEXT,
            granular_cast TEXT,
            other1 TEXT,
            other2 TEXT,
            other3 TEXT,
            puncture_fluid_glucose REAL,
            troponin_t REAL,
            FOREIGN KEY(patient_id) REFERENCES patient(patient_id)
            '''
        
        with self.get_connection() as conn:
            
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {self.PATIENT_TABLE} ({sql_patient_colmuns})"
            )
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {self.RESULT_TABLE} ({sql_result_colmuns})"
            )
            conn.commit()
    
    def insert_patient(self, column_names, values):

        column_str = ','.join(column_names)
        placeholders = ','.join(['?'] * len(column_names))
        
        sql = (
            f"INSERT INTO {self.PATIENT_TABLE} ({column_str})"
            f"VALUES ({placeholders})"
        )

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()

            return cursor.lastrowid    

    def select_patient(self, patient_id=None):

        sql = f"SELECT * FROM {self.PATIENT_TABLE}"
        if patient_id is not None:
            sql += f" where patient_id=?"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if patient_id is None: 
                cursor.execute(sql)
            else:
                cursor.execute(sql, (patient_id,))

        if patient_id is None:
            table_data = cursor.fetchall()
            val =[dict(row) for row in table_data]
            return [dict(row) for row in table_data]
        else:
            table_data = cursor.fetchone()
            return dict(table_data) if table_data else None
        
    def insert_result(self, column_names, values):

        column_str = ','.join(column_names)
        placeholders = ','.join(['?'] * len(column_names))

        sql = (
            f"INSERT INTO {self.RESULT_TABLE} ({column_str})"
            f"VALUES ({placeholders})"
        )

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()

            return cursor.lastrowid

    def select_result(self, result_id=None, patient_id=None):
        sql = f"SELECT * FROM {self.RESULT_TABLE}"
        value = None

        if result_id is not None:
            sql += f" where result_id=?"
            value = result_id
        elif patient_id is not None:
            sql += f" where patient_id=?"
            value = patient_id

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if value is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, (value,))

        table_data = cursor.fetchall()
        val = [dict(row) for row in table_data]
        return [dict(row) for row in table_data]
