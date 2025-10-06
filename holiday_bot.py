import requests
import datetime
import csv
import io
import os

def main():
    # Получаем настройки из секретов GitHub
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL')
    sheet_url = os.getenv('GOOGLE_SHEET_URL')
    
    print("🤖 Запуск проверки праздников...")
    
    try:
        # Преобразуем ссылку для CSV
        csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
        response = requests.get(csv_url)
        csv_data = response.content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(csv_data))
        
        today = datetime.datetime.now().strftime("%m-%d")
        today_events = []
        
        for row in reader:
            date = row.get('Дата (ММ-ДД)', '').strip()
            if date == today:
                event = {
                    'holiday': row.get('Что за праздник', 'Праздник'),
                    'person': row.get('Кого поздравить', ''),
                    'phone': row.get('Телефон', '')
                }
                today_events.append(event)
        
        if today_events:
            message = format_message(today_events)
            send_telegram_message(telegram_token, channel_id, message)
            print("✅ Праздники найдены и отправлены!")
        else:
            print("📭 Сегодня праздников нет")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def format_message(events):
    """Форматируем сообщение"""
    message = "🎉 <b>Сегодняшние праздники:</b>\n\n"
    
    for event in events:
        message += f"• <b>{event['holiday']}</b>\n"
        
        person = event.get('person', '')
        phone = event.get('phone', '')
        
        if person and person.lower() not in ['всех', 'все', '-', '']:
            message += f"  🎁 Поздравить: <b>{person}</b>\n"
            if phone and phone != '-':
                message += f"  📞 Телефон: <code>{phone}</code>\n"
        else:
            message += f"  🎁 Поздравляем <b>всех</b>!\n"
        
        message += "\n"
    
    return message + "Хорошего дня! ✨"

def send_telegram_message(token, chat_id, text):
    """Отправляем сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    response = requests.post(url, data=data)
    return response.json()

if __name__ == "__main__":
    main()