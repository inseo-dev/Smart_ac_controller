from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pymysql
import json
from flask_cors import CORS
from enum import Enum
import re

def get_connection():
    return pymysql.connect(
        host="database-1.cts2qeeg0ot5.ap-northeast-2.rds.amazonaws.com",
        user="kevin",
        db="sac",
        password="spreatics*",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

app = Flask(__name__)
# 프론트엔드 모든 요청 허용
CORS(app)


############################################
# frontend <-> server
############################################

# 사용자 생성
@app.route('/fr_serv/users', methods = ['POST'])
def create_user():
    data = request.get_json(silent=True) or {}
    user_name = data.get("user_name")
    temp_preferred = data.get("temp_preferred", None)
    ble_address = data.get("ble_address", None)

    # 필수 정보 누락
    if not user_name:
         return jsonify({
                "result":"failed",
                "fail_reason": "missing_required_field"
            }),400
    
    # 타입 불일치
    if not isinstance(user_name, str):
        return jsonify({
            "result": "failed",
            "fail_reason": "invalid_type"
        }), 400
    if temp_preferred is not None and not isinstance(temp_preferred, (int, float)):
        return jsonify({
            "result": "failed",
            "fail_reason": "invalid_type"
        }), 400
    
    # BLE 주소 형식 오류
    if ble_address:
        pattern = r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
        if not re.match(pattern, ble_address):
            return jsonify({
                "result": "failed",
                "fail_reason": "invalid_ble_address_format"
            }), 400
    
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            # BLE 주소 중복
            if ble_address is not None and ble_address.strip() != "":
                sql = """
                SELECT count(*) as count
                FROM user_info
                WHERE ble_address = %s;
                """
                cursor.execute(sql, (ble_address,))

                if cursor.fetchone()['count'] > 0:
                     return jsonify({
                          "result": "failed",
                          "fail_reason": "duplicate_ble_address"
                     }),400
                     
            # DB에 정보 생성
            sql = """
            INSERT INTO user_info (user_name, temp_preferred, ble_address)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql,(user_name, temp_preferred, ble_address))
            
            conn.commit()

            return jsonify({
                "result": "success", 
                "fail_reason": None
            })
    # 서버 내부 문제
    except Exception as e:
        print("에러 발생: ", str(e))
        return jsonify({
            "result": "failed",
            "user_info": None,
            "fail_reason": "internal_server_error"
        }),500

# 사용자 목록 조회
@app.route('/serv_fr/users', methods=['GET'])
def get_user_list():    
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            sql = """
            SELECT user_name , temp_preferred, ble_address
            FROM user_info
            ORDER BY user_name;
            """
            cursor.execute(sql)
            rows = cursor.fetchall()

            return jsonify({
                "result": "success", 
                "fail_reason": None,
                "user_info": rows
            })
    # 서버 내부 문제
    except Exception as e:
        print("에러 발생: ", str(e))
        return jsonify({
            "result": "failed",
            "user_info": None,
            "fail_reason": "internal_server_error"
        })

# 사용자 수정
@app.route('/fr_serv/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    data = request.get_json(silent=True) or {}
    user_name = data.get("user_name","")
    temp_preferred = data.get("temp_preferred", None)
    ble_address = data.get("ble_address")
    print(ble_address)
    # 타입 불일치
    if not isinstance(user_name, str):
        return jsonify({
            "result": "failed",
            "fail_reason": "invalid_type"
        }), 400
    if temp_preferred is not None and not isinstance(temp_preferred, (int, float)):
        return jsonify({
            "result": "failed",
            "fail_reason": "invalid_type"
        }), 400
    
    # BLE 주소 형식 오류
    if ble_address:
        pattern = r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"
        if not re.match(pattern, ble_address):
            return jsonify({
                "result": "failed",
                "fail_reason": "invalid_ble_address_format"
            }), 400
    
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            # BLE 주소 중복
            if ble_address is not None and ble_address.strip() != "":
                sql = """
                SELECT count(*) as count
                FROM user_info
                WHERE ble_address = %s;
                """
                cursor.execute(sql, (ble_address,))

                if cursor.fetchone()['count'] > 0:
                     return jsonify({
                          "result": "failed",
                          "fail_reason": "duplicate_ble_address"
                     }),400
                     
            # DB에 정보 업데이트
            if user_name:
                cursor.execute("UPDATE user_info SET user_name=%s WHERE user_id=%s", (user_name, user_id))
            if temp_preferred is not None:
                cursor.execute("UPDATE user_info SET temp_preferred=%s WHERE user_id=%s", (temp_preferred, user_id))
            if ble_address:
                cursor.execute("UPDATE user_info SET ble_address=%s WHERE user_id=%s", (ble_address, user_id))
            
            conn.commit()

            return jsonify({
                "result": "success", 
                "fail_reason": None
            }),200
    # 서버 내부 문제
    except Exception as e:
        print("에러 발생: ", str(e))
        return jsonify({
            "result": "failed",
            "user_info": None,
            "fail_reason": "internal_server_error"
        }),500


# 사용자 삭제
@app.route('/fr_serv/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):    
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            sql = """
            DELETE FROM user_info
            WHERE user_id = %s
            """
            cursor.execute(sql,(user_id,))
            conn.commit()

            return jsonify({
                "result": "success", 
                "fail_reason": None
            })
    # 서버 내부 문제
    except Exception as e:
        print("에러 발생: ", str(e))
        return jsonify({
            "result": "failed",
            "fail_reason": "internal_server_error"
        })

# 에어컨 상태 조회 
@app.route('/serv_fr/ac/state', methods=['GET'])
def get_ac_state():    
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            sql = """
            SELECT *
            FROM ac_state
            ORDER BY timestamp DESC
            LIMIT 1;
            """
            cursor.execute(sql)
            row = cursor.fetchone()

            return jsonify({
                "result": "success", 
                "fail_reason": None,
                "ac_state": {
                    "ac_action":row["ac_action"],
		            "ac_temp":row["ac_temp"]
                }
            })
    # 서버 내부 문제
    except Exception as e:
        print("에러 발생: ", str(e))
        return jsonify({
            "result": "failed",
            "ac_state": None,
            "fail_reason": "internal_server_error"
        })
    
# 현재 설정 온도 조회
@app.route('/serv_fr/env/target_temp', methods=['GET'])
def get_target_temp():    
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            sql = """
            
            """
            cursor.execute(sql)
            rows = cursor.fetchall()

            #더미데이터
            return jsonify({
                "result": "success", 
                "fail_reason": None,
                "target_temp": 25 
            })
    # 서버 내부 문제
    except Exception as e:
        print("에러 발생: ", str(e))
        return jsonify({
            "result": "failed",
            "target_temp": None,
            "fail_reason": "internal_server_error"
        })
    
# 현재 공간에 있는 사용자 조회(rssi 범위 : 0 ~ -70)
@app.route('/serv_fr/detections/users', methods=['GET'])
def get_users_in_room():    
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            sql = """
            SELECT user_name, temp_preferred, ble_address
            FROM user_presence up
            JOIN user_info ui 
            ON up.user_id = ui.user_id 
            WHERE ble_rssi > -70
            GROUP BY up.user_id
            ORDER BY max(detected_time) DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()

            return jsonify({
                "result": "success", 
                "fail_reason": None,
                "user_info": rows
            })
    # 서버 내부 문제
    except Exception as e:
        print("에러 발생: ", str(e))
        return jsonify({
            "result": "failed",
            "user_info": None,
            "fail_reason": "internal_server_error"
        })

app.run(debug=True, host='0.0.0.0', port=5000)
