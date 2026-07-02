# bot_api.py - бот для приёма заявок с сайта
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime
import logging
import sys

# ==================== НАСТРОЙКА ====================
TELEGRAM_TOKEN = '8676360269:AAEHF1SkSAXPIqJwJMqzh49IMz3uPUs8PTY'
ADMIN_CHAT_ID = '8284059710'

# НАСТРОЙКА VK
VK_TOKEN = 'vk1.a.aPyqTRyxAa1pjWmhqlB-1G4Su6SaeoFTX5BUvsAecurIizINMbaE-Dopn3G7Znu7twuYn6NpWJMtaWHbHD7KFPhCJ5xiXVYutUPJ7HQKkPok5Kkr0hXQOaM17z5uOudf8L3PZA3NBHJ73uhICzkYtXmFnTWG3_I1TlenRgkEEggEHuzt8qhea49osOOXvep54TNM8jiCeZDI-xbulVC8yQ'
VK_USER_ID = '598049412'

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
app = Flask(__name__)
CORS(app)

# ПОЛНОСТЬЮ ОТКЛЮЧАЕМ ВСЕ ЛОГИ
log = logging.getLogger('werkzeug')
log.disabled = True

# Отключаем вывод в консоль
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger('').handlers = []
logging.getLogger('').addHandler(NullHandler())

# Создаём свой простой логгер только для заявок
def log_lead(message):
    """Простой вывод только для заявок"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] 📨 {message}")

# ==================== ФУНКЦИИ ОТПРАВКИ ====================

def send_to_telegram(message):
    """Отправляет сообщение в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            'chat_id': ADMIN_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        return None

def send_to_vk(message):
    """Отправляет сообщение в VK"""
    try:
        clean_message = message.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '')
        
        url = "https://api.vk.com/method/messages.send"
        params = {
            'v': '5.131',
            'access_token': VK_TOKEN,
            'peer_id': VK_USER_ID,
            'message': clean_message,
            'random_id': int(datetime.now().timestamp() * 1000)
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('error'):
            return None
        return data
    except Exception as e:
        return None

def format_lead_message(data):
    """Форматирует заявку для отправки"""
    lead_type = data.get('type', 'unknown')
    
    if lead_type == 'full':
        return (
            f"🔔 <b>Новая заявка (расчёт стоимости)</b>\n\n"
            f"👤 <b>Имя:</b> {data.get('name', 'Не указано')}\n"
            f"📞 <b>Телефон:</b> {data.get('phone', 'Не указан')}\n"
            f"📐 <b>Площадь:</b> {data.get('area', 'Не указана')} м²\n"
            f"📍 <b>Адрес:</b> {data.get('address', 'Не указан')}\n"
            f"📝 <b>Сообщение:</b> {data.get('message', '—')}\n"
            f"🕒 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
    elif lead_type == 'quick':
        return (
            f"🔔 <b>Новая заявка</b>\n\n"
            f"👤 <b>Имя:</b> {data.get('name', 'Не указано')}\n"
            f"📞 <b>Телефон:</b> {data.get('phone', 'Не указан')}\n"
            f"🕒 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
    else:
        return (
            f"🔔 <b>Новая заявка</b>\n\n"
            f"👤 <b>Имя:</b> {data.get('name', 'Не указано')}\n"
            f"📞 <b>Телефон:</b> {data.get('phone', 'Не указан')}\n"
            f"🕒 <b>Время:</b> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )

def format_vk_message(data):
    """Форматирует заявку для VK"""
    lead_type = data.get('type', 'unknown')
    
    if lead_type == 'full':
        return (
            f"🔔 Новая заявка (расчёт стоимости)\n\n"
            f"👤 Имя: {data.get('name', 'Не указано')}\n"
            f"📞 Телефон: {data.get('phone', 'Не указан')}\n"
            f"📐 Площадь: {data.get('area', 'Не указана')} м²\n"
            f"📍 Адрес: {data.get('address', 'Не указан')}\n"
            f"📝 Сообщение: {data.get('message', '—')}\n"
            f"🕒 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
    elif lead_type == 'quick':
        return (
            f"🔔 Новая заявка\n\n"
            f"👤 Имя: {data.get('name', 'Не указано')}\n"
            f"📞 Телефон: {data.get('phone', 'Не указан')}\n"
            f"🕒 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
    else:
        return (
            f"🔔 Новая заявка\n\n"
            f"👤 Имя: {data.get('name', 'Не указано')}\n"
            f"📞 Телефон: {data.get('phone', 'Не указан')}\n"
            f"🕒 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )

def send_lead_to_all(data):
    """Отправляет заявку во все каналы"""
    results = {}
    
    tg_message = format_lead_message(data)
    vk_message = format_vk_message(data)
    
    # Отправляем в Telegram
    tg_result = send_to_telegram(tg_message)
    results['telegram'] = tg_result is not None
    
    # Отправляем в VK
    vk_result = send_to_vk(vk_message)
    results['vk'] = vk_result is not None
    
    return results

# ==================== API ЭНДПОИНТЫ ====================

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'status': 'ok',
        'message': 'API для приёма заявок на стяжку пола',
        'endpoints': {
            '/lead': 'POST - принять заявку',
            '/send_test': 'GET - отправить тестовое сообщение'
        }
    })

@app.route('/lead', methods=['POST'])
def receive_lead():
    """Принимает заявку с сайта"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('name') or not data.get('phone'):
            return jsonify({
                'error': 'Имя и телефон обязательны'
            }), 400
        
        if data.get('area') or data.get('address'):
            lead_type = 'full'
        else:
            lead_type = 'quick'
        
        lead_data = {
            'type': lead_type,
            'name': data.get('name'),
            'phone': data.get('phone'),
            'area': data.get('area', ''),
            'address': data.get('address', ''),
            'message': data.get('message', ''),
            'timestamp': datetime.now().isoformat(),
            'source': 'website'
        }
        
        # Отправляем уведомления
        send_lead_to_all(lead_data)
        
        # ЕДИНСТВЕННЫЙ ЛОГ - только когда заявка отправлена
        log_lead(f"Заявка от {lead_data['name']} ({lead_data['phone']})")
        
        return jsonify({
            'status': 'success',
            'message': 'Заявка принята'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send_test', methods=['GET'])
def send_test():
    """Отправляет тестовое сообщение"""
    test_message = (
        "🧪 <b>Тестовое сообщение</b>\n\n"
        "Бот работает и готов принимать заявки!\n"
        f"🕒 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    )
    
    results = {}
    
    tg_result = send_to_telegram(test_message)
    results['telegram'] = tg_result is not None
    
    vk_result = send_to_vk(test_message.replace('<b>', '').replace('</b>', ''))
    results['vk'] = vk_result is not None
    
    log_lead("Тестовое сообщение отправлено")
    
    return jsonify({
        'status': 'test_sent',
        'results': results
    })

# ==================== ЗАПУСК ====================
if __name__ == '__main__':
    print("=" * 60)
    print("🤖 TELEGRAM + VK БОТ API")
    print("=" * 60)
    print("")
    print("✅ Бот запущен!")
    print("🌐 API: http://localhost:5000")
    print("📋 POST /lead - Отправить заявку")
    print("")
    print("📌 Логируются только заявки:")
    print("   [18:30:15] 📨 Заявка от Александр (+79192822197)")
    print("")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("-" * 60)
    
    # Запускаем без логов
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)