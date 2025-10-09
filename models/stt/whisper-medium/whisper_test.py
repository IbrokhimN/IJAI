from whismedium import VoiceListener

def main():
    print("🎤 Тест запуска VoiceListener...\n")

    listener = VoiceListener(
        model_size="small",
        silence_threshold=0.01,
        silence_duration=2.5,
        chunk_duration=0.25,
        language="ru"
    )

    print("✅ VoiceListener успешно инициализирован.\n")
    print("🎧 Говори что-нибудь! (нажми Ctrl+C чтобы выйти)\n")

    try:
        while True:
            text = listener.listen_once()
            if text:
                print(f"Распознан текст: {text}")
            else:
                print("(тишина)")
    except KeyboardInterrupt:
        print("\nЗавершено пользователем.")

if __name__ == "__main__":
    main()

