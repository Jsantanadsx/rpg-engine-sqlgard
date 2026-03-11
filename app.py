import os
import oracledb
from flask import Flask, render_template, redirect

app = Flask(__name__)

def get_connection():
    return oracledb.connect(
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        dsn=os.environ.get('DB_DSN')
    )

@app.route('/')
def index():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT nome, classe, hp_atual, hp_max, status FROM TB_HEROIS")

    herois = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('index.html', herois=herois)

@app.route('/processar')
def processar():

    bloco_plsql_prox_rodada = """
    DECLARE
        v_dano_nevoa NUMBER := 10; -- Dano causado pela névoa
    BEGIN

        FOR r IN (
            SELECT id_heroi
            FROM TB_HEROIS
            WHERE status = 'ATIVO'
        ) LOOP

            UPDATE TB_HEROIS
            SET hp_atual = hp_atual - v_dano_nevoa
            WHERE id_heroi = r.id_heroi;

            UPDATE TB_HEROIS
            SET status = 'CAÍDO'
            WHERE id_heroi = r.id_heroi
            AND hp_atual <= 0;
        
        END LOOP;

        COMMIT;
    END;
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(bloco_plsql_prox_rodada)

    cursor.close()
    conn.close()

    return redirect("/")

@app.route('/resetar')
def resetar():

    bloco_plsql_reset = """
    BEGIN
        UPDATE TB_HEROIS -- Reseta os heróis para o estado inicial
        SET hp_atual = hp_max,
            status = 'ATIVO';
        COMMIT;
    END;
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(bloco_plsql_reset)

    cursor.close()
    conn.close()

    return redirect("/")

if __name__ == '__main__':
    app.run()