from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import pymysql
import json
from flask_cors import CORS
from enum import Enum

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

# 사용자 목록 조회
@app.route('/serv_fr/users', methods=['GET'])
def get_user_list():    
    try:
        #conn = get_connection()
        
        #with conn.cursor() as cursor:
        #    sql = """"""
        #    cursor.execute(sql)
        #    rows = cursor.fetchall()

            #더미데이터
            return jsonify({
                "result": "success", 
                "fail_reason": None,
                "user_info": [
                    {"user_name":"홍길동", "temp_preferred":25, "ble_address":"AA:BB:CC:DD:EE:FF"},
                    {"user_name":"김철수", "temp_preferred":22, "ble_address":"12:34:56:78:9A:BC"},
                    {"user_name":"최영희", "temp_preferred":26, "ble_address":"C0:98:E5:00:12:7F"}
                ]
            })
    # 서버 내부 문제
    except Exception as e:
        print("에러 발생: ", str(e))
        return jsonify({
            "result": "failed",
            "user_info": None,
            "fail_reason": "internal_server_error"
        })
    
# 에어컨 상태 조회 
@app.route('/serv_fr/ac/state', methods=['GET'])
def get_ac_state():    
    try:
        #conn = get_connection()
        
        #with conn.cursor() as cursor:
        #    sql = """"""
        #    cursor.execute(sql)
        #    rows = cursor.fetchall()

            #더미데이터
            return jsonify({
                "result": "success", 
                "fail_reason": None,
                "ac_state": {
                    "ac_action":"ON",
		            "ac_temp":25
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
        #conn = get_connection()
        
        #with conn.cursor() as cursor:
        #    sql = """"""
        #    cursor.execute(sql)
        #    rows = cursor.fetchall()

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
    
# 현재 공간에 있는 사용자 조회
@app.route('/serv_fr/detections/users', methods=['GET'])
def get_users_in_room():    
    try:
        #conn = get_connection()
        
        #with conn.cursor() as cursor:
        #    sql = """"""
        #    cursor.execute(sql)
        #    rows = cursor.fetchall()

            #더미데이터
            return jsonify({
                "result": "success", 
                "fail_reason": None,
                "user_info": [
                    {"user_name":"김철수", "temp_preferred":22, "ble_address":"12:34:56:78:9A:BC"},
                    {"user_name":"최영희", "temp_preferred":26, "ble_address":"C0:98:E5:00:12:7F"}
                ]
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
