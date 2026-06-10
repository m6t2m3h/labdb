import os
import logging
import sqlite3
import pandas as pd
from DatabaseDefinition import DatabaseDefinition

class TableDataRepository(DatabaseDefinition):

    def __init__(self):
        self.db_path = self.DATA_BASE_DIR + self.DATA_BASE_NAME + ".db"
        self.logger = logging.getLogger(__name__) 
        os.makedirs(self.DATA_BASE_DIR, exist_ok=True)

    def create_table(self):

        sql_colmuns = '''id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            troponin_t REAL
            '''
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {self.DATA_BASE_NAME} ({sql_colmuns})"
            )
            conn.commit()

    def insert_table_data(self, column_names, values):

        column_str = ','.join(column_names)
        placeholders = ','.join(['?'] * len(column_names))
        
        sql = (
            f"INSERT INTO {self.DATA_BASE_NAME} ({column_str})"
            f"VALUES ({placeholders})"
        )

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()

    def select_table_data(self):
        sql = f"SELECT * FROM {self.DATA_BASE_NAME}"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
        table_data = cursor.fetchall()
        return table_data


    # pandas版のテーブル表示
    def preview_table_data(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            f"SELECT * FROM {self.DATA_BASE_NAME}",
            conn
        )
        print(df)