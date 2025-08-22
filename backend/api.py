from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pymysql
import json
from flask_cors import CORS
from enum import Enum
import re
import pytz

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

# 사용자 생성 api
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
    # 온도 범위 초과
    if temp_preferred > 30 and temp_preferred < 18:
        return jsonify({
            "result": "failed",
            "fail_reason": "temperature out of range"
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

# 사용자 목록 조회 api
@app.route('/serv_fr/users', methods=['GET'])
def get_user_list(): 
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            sql = """
            SELECT user_id, user_name , temp_preferred, ble_address
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

# 사용자 수정 api
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
    if temp_preferred is not None:
        # 타입 불일치
        if not isinstance(temp_preferred, (int, float)):
            return jsonify({
                "result": "failed",
                "fail_reason": "invalid_type"
            }), 400
        
        # 온도범위초과
        if temp_preferred > 30 or temp_preferred < 18:
            return jsonify({
                "result": "failed",
                "fail_reason": "temperature out of range"
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


# 사용자 삭제 api
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

# 에어컨 상태 조회 api
@app.route('/serv_fr/ac/state', methods=['GET'])
def get_ac_state():    
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            sql = """
            SELECT ac_action, ac_temp
            FROM ac_state
            ORDER BY timestamp DESC
            LIMIT 1;
            """
            cursor.execute(sql)
            row = cursor.fetchone()

            return jsonify({
                "result": "success", 
                "fail_reason": None,
                "ac_state": row
            })
    # 서버 내부 문제
    except Exception as e:
        print("에러 발생: ", str(e))
        return jsonify({
            "result": "failed",
            "ac_state": None,
            "fail_reason": "internal_server_error"
        })
    
# 현재 설정 온도 조회 api (우선 방안에 있는 사람들 선호온도 평균으로 구함/소수점 첫째자리 반올림) 
@app.route('/serv_fr/env/target_temp', methods=['GET'])
def get_target_temp():   
    # 한국 시간 설정
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.now(kst)
    now_time = now_kst.strftime("%Y-%m-%d %H:%M:%S") 
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            sql = """
            SELECT round(AVG(temp_preferred),0) as avg_temp
            FROM(
                SELECT 
                    up.user_id, 
                    avg(NULLIF(ble_rssi,-128)) AS avg_rssi
                FROM user_presence up 
                JOIN user_info u
                ON up.user_id = u.user_id
                WHERE up.detected_time >= %s - INTERVAL 15 SECOND
                GROUP BY up.user_id
                HAVING avg_rssi >= -75
            ) t
            JOIN user_info u
            ON t.user_id = u.user_id
            """
            cursor.execute(sql,(now_time))
            row = cursor.fetchone()

            return jsonify({
                "result": "success", 
                "fail_reason": None,
                "target_temp": row["avg_temp"]
            })
    # 서버 내부 문제
    except Exception as e:
        print("에러 발생: ", str(e))
        return jsonify({
            "result": "failed",
            "target_temp": None,
            "fail_reason": "internal_server_error"
        })
    
# 현재 공간에 있는 사용자 조회 api(rssi 범위 : 0 ~ -75 / 현재시간부터 10분안)
@app.route('/serv_fr/detections/users', methods=['GET'])
def get_users_in_room():    
    # 한국 시간 설정
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.now(kst)
    now_time = now_kst.strftime("%Y-%m-%d %H:%M:%S")

    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            sql = """
            SELECT t.user_id, t.user_name, t.distance_m
            FROM(
                SELECT 
                    up.user_id, 
                    u.user_name,
                    MAX(up.detected_time) AS last_detected,
                    avg(NULLIF(ble_rssi,-128)) AS avg_rssi,
                    POW(10, (-59 - avg(NULLIF(ble_rssi,-128))) / (10 * 2.7)) AS distance_m
                FROM user_presence up 
                JOIN user_info u
                ON up.user_id = u.user_id
                WHERE up.detected_time >= %s - INTERVAL 10 MINUTE
                GROUP BY user_id
                HAVING avg_rssi >= -75
            ) t
            WHERE t.last_detected >= %s - INTERVAL 15 SECOND;
            """
            cursor.execute(sql,(now_time, now_time))
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
    
############################################
# arduino -> server
############################################

# 블루투스 감지 전송 api
@app.route('/ardu_serv/detections', methods = ['POST'])
def post_ble():
    data = request.get_json(silent=True) or {}
    ble_address = data.get("ble_address", None)
    ble_rssi = data.get("ble_rssi",None)

    # 한국 시간 설정
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.now(kst)
    now_time = now_kst.strftime("%Y-%m-%d %H:%M:%S")

    detected_time = now_time

    # 필수 정보 누락
    if not ble_address or not ble_rssi or not detected_time:
         return jsonify({
                "result":"failed",
                "fail_reason": "missing_required_field"
            }),400
    
    # 타입 불일치
    if ble_rssi is not None and not isinstance(ble_rssi, (int, float)):
        return jsonify({
            "result": "failed",
            "fail_reason": "invalid_type"
        }), 400
    
    # rssi 범위 오류
    if ble_rssi > 0 or ble_rssi < -100:
        return jsonify({
            "result": "failed",
            "fail_reason": "ble_rssi_out_of_range"
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
            # 같은 시간일 경우 에러
            time_sql = """
            SELECT count(*)
            FROM user_presence
            WHERE detected_time = %s
            """
            cursor.execute(time_sql, (detected_time,))
            if cursor.fetchone()["count(*)"] != 0:
                return jsonify({
                          "result": "failed",
                          "fail_reason": "duplicate_time"
                     }),400

            # DB에서 사용자 id 찾음
            search_sql = """
            SELECT user_id
            FROM user_info
            WHERE ble_address = %s
            """
            cursor.execute(search_sql, (ble_address,))
            row = cursor.fetchone()

            # DB등록된 사용자인지 BLE 주소 확인
            if not row:
                return jsonify({
                          "result": "failed",
                          "fail_reason": "BLE_address_is_not_registered"
                     }),400
            
            search_user_id = row["user_id"] 

            # DB에 정보 생성
            sql = """
            INSERT INTO user_presence (user_id, ble_rssi, detected_time)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql,(search_user_id, ble_rssi, detected_time))
            
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
        }),500

# 에어컨 작동 정보 전송 api
@app.route('/ardu_serv/logs', methods = ['POST'])
def post_ac_action():
    data = request.get_json(silent=True) or {}
    ac_action = data.get("ac_action", None)
    ac_temp = None

    # 한국 시간 설정
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.now(kst)
    now_time = now_kst.strftime("%Y-%m-%d %H:%M:%S")

    # 필수 정보 누락
    if not ac_action:
         return jsonify({
                "result":"failed",
                "fail_reason": "missing_required_field"
            }),400
    
    # 타입 불일치
    if ac_action is not None and not isinstance(ac_action, (str)):
        return jsonify({
            "result": "failed",
            "fail_reason": "invalid_type"
        }), 400
    
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            # 같은 시간일 경우 에러
            time_sql = """
            SELECT count(*)
            FROM ac_state
            WHERE timestamp = %s
            """
            cursor.execute(time_sql, (now_time,))
            if cursor.fetchone()["count(*)"] != 0:
                return jsonify({
                          "result": "failed",
                          "fail_reason": "duplicate_time"
                     }),400
            # OFF일 경우
            if ac_action[0] == "0":
                ac_action = "OFF"
            # ON일 경우
            elif ac_action[0] == "1":
                ac_action = "ON"
            # t일 경우
            elif ac_action[0] == "t":
                ac_temp = float(ac_action[1:])
                ac_action = "ON"
                auto_action = "SET_TEMP"
                
            # DB에 정보 생성
            state_sql = """
            INSERT INTO ac_state (ac_action, ac_temp, timestamp)
            VALUES (%s, %s, %s)
            """
            cursor.execute(state_sql,(ac_action, ac_temp, now_time))

            log_sql = """
            INSERT INTO auto_temp_log (user_id, auto_time, auto_action, auto_temp)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(log_sql,(1,now_time , auto_action, ac_temp))
            
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
        }),500

# ir 코드
ir_code = {
    "0x83D6D202":"off",
    "0x494AECFE":"on",
    "0xC40CEF6F":"on",
    "0xD0841BCE":"on",
    "0xBB68F8D3":"on",
    "0xD55D206A":"on",
    "0xA13493CD":"on",
    "0x9E0385F8":"on",
    "0xBDF9AA79":"on",
    "0xDBEDD85C":"on",
    "0xD29E0109":"on",
    "0xB4EEF966":"on",
    "0xDE3DD4D":"on",
    "0x2BD80B30":"on",
    
    "0xD3E0CB48":"30",
    "0xB5EC9D65":"29",
    "0xFE0F2A24":"28",
    "0xD29E0109":"27",
    "0xFB36156":"26",
    "0xF5BF39BF":"25",
    "0x59D52730":"24",
    "0x449BEA4D":"23",
    "0xC36335F2":"22",
    "0xA96F0E5B":"21",
    "0x68E4752C":"20",
    "0x2965DF09":"19",
    "0x14B34D1C":"18"
}
# 리모컨 조작 정보 전송 api
@app.route('/ardu_serv/ir', methods = ['POST'])
def post_ir():
    data = request.get_json(silent=True) or {}
    raw_signal_data = data.get("raw_signal_data", None)
    ac_action = ir_code.get(raw_signal_data, None)
    target_temp = None

    # 한국 시간 설정
    kst = pytz.timezone("Asia/Seoul")
    now_kst = datetime.now(kst)
    recorded_time = now_kst.strftime("%Y-%m-%d %H:%M:%S")
    
    # 필수 정보 누락
    if not raw_signal_data:
         return jsonify({
                "result":"failed",
                "fail_reason": "missing_required_field"
            }),400
    # 잘못된 ir코드
    if ac_action is None:
        return jsonify({
                "result":"failed",
                "fail_reason": "wrong_ir_code"
            }),400
    
    # 타입 불일치
    if raw_signal_data is not None and not isinstance(raw_signal_data, (str)):
        return jsonify({
            "result": "failed",
            "fail_reason": "invalid_type"
        }), 400
    
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            # 같은 시간일 경우 에러
            time_sql = """
            SELECT count(*)
            FROM ir_logs
            WHERE recorded_time = %s
            """
            cursor.execute(time_sql, (recorded_time,))
            if cursor.fetchone()["count(*)"] != 0:
                return jsonify({
                          "result": "failed",
                          "fail_reason": "duplicate_time"
                     }),400
            if ac_action == "off":
                decoded_action = "OFF"
            elif ac_action == "on":
                decoded_action = "ON"
            elif ac_action in ["18","19","20","21","22","23","24","25","26","27","28","29","30"]:
                decoded_action = "ON"
            # DB에 정보 생성
            sql = """
            INSERT INTO ir_logs (raw_signal_data, decoded_action, recorded_time)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql,(raw_signal_data, decoded_action, recorded_time))
            
            if ac_action == "off":
                oper_action = "OFF"
            elif ac_action == "on":
                oper_action = "ON"
                target_temp = 25    
            elif ac_action in ["18","19","20","21","22","23","24","25","26","27","28","29","30"]:
                oper_action = "SET_TEMP"
                target_temp = float(ac_action)

            sql = """
            INSERT INTO oper_temp_log (oper_action, target_temp, oper_time)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql,(oper_action, target_temp, recorded_time))

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
        }),500
    
############################################
# server -> arduino
############################################

# 에어컨 설정 호출 api
@app.route('/serv_ardu/ac/users', methods=['GET'])
def get_ac_temp():    
    try:
        conn = get_connection()
        
        with conn.cursor() as cursor:
            sql = """
            SELECT round(AVG(temp_preferred),0) AS avg_temp_preferred
            FROM(
			    SELECT ui.temp_preferred
                FROM user_presence up
                JOIN user_info ui 
                ON up.user_id = ui.user_id 
                WHERE ble_rssi > -70
                GROUP BY up.user_id
                ORDER BY max(detected_time) DESC
            ) t;
            """
            cursor.execute(sql)
            row = cursor.fetchone()

            if row is None:
                return jsonify({
                    "result": "failed",
                    "avg_temp_preferred": None,
                    "fail_reason": "no_avg_temp_preferred" 
                })

            return jsonify({
                "result": "success", 
                "fail_reason": None,
                "avg_temp_preferred": row["avg_temp_preferred"]
            })
    # 서버 내부 문제
    except Exception as e:
        print("에러 발생: ", str(e))
        return jsonify({
            "result": "failed",
            "avg_temp_preferred": None,
            "fail_reason": "internal_server_error"
        })
    



app.run(debug=True, host='0.0.0.0', port=5000)
