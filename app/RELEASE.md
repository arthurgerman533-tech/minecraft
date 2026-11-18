# Как выпустить приложение PaxVanila в Google Play и App Store

Приложение написано на Flutter (папка `app/`). Тексты, недели, механики и лор берутся из `content/paxvanila.json`, `лор/` и `гайды/`. После правок контента запустите `python tools/build_site.py`: он обновит и сайт (`docs/`), и ассеты приложения (`app/assets/`).

## 1. Перед первым выпуском

1. Заполните в `content/paxvanila.json` поля `serverAddress`, `discordUrl`, `launchDate` (и `mapUrl`, если есть карта). Запустите `python tools/build_site.py`.
2. Включите сайт: на GitHub откройте Settings → Pages, выберите ветку `main` и папку `/docs`. Через минуту сайт будет по адресу `https://<логин>.github.io/<репозиторий>/`. На бесплатном плане Pages работает только для **публичного** репозитория.
3. Ссылка на политику конфиденциальности для магазинов: `https://<логин>.github.io/<репозиторий>/privacy.html`.

## 2. Что поставить на компьютер

- Flutter SDK 3.50 или новее: https://docs.flutter.dev/get-started/install
- Для Android: Android Studio (в ней Android SDK).
- Для iOS: Mac с Xcode. **Без Mac собрать ipa нельзя.** Можно взять облачную сборку, например Codemagic.

Проверка: `flutter doctor`.

## 3. Android (Google Play)

1. Аккаунт разработчика Google Play: https://play.google.com/console, разовый платёж **25$**.
2. Ключ подписи (один раз, храните файл и пароль в надёжном месте, без них обновить приложение нельзя):
   ```
   keytool -genkey -v -keystore paxvanila.jks -keyalg RSA -keysize 2048 -validity 10000 -alias paxvanila
   ```
3. Создайте `app/android/key.properties` (он не должен попасть в git):
   ```
   storePassword=...
   keyPassword=...
   keyAlias=paxvanila
   storeFile=../../paxvanila.jks
   ```
   и подключите его в `android/app/build.gradle.kts` в блоке `signingConfigs` (инструкция: https://docs.flutter.dev/deployment/android).
4. Сборка: `cd app && flutter build appbundle`. Файл: `build/app/outputs/bundle/release/app-release.aab`.
5. В Play Console: создать приложение, загрузить aab, заполнить описание, скриншоты (минимум 2 с телефона), иконку 512×512 (`docs/icons/icon-512.png`), баннер 1024×500, анкету о возрастном рейтинге, раздел «Безопасность данных» (данные не собираются) и ссылку на политику конфиденциальности.
6. Новые личные аккаунты сначала проходят закрытое тестирование: нужно 12 тестировщиков в течение 14 дней. Позовите игроков из Discord.

Идентификатор приложения: `com.paxvanila.paxvanila`. Его нельзя поменять после первой публикации.

## 4. iOS (App Store)

1. Apple Developer Program: https://developer.apple.com/programs/, **99$ в год**.
2. На Mac: `cd app && open ios/Runner.xcworkspace`, в Xcode выберите свою команду (Signing & Capabilities), Bundle ID `com.paxvanila.paxvanila`.
3. Сборка: `flutter build ipa`. Загрузка через Xcode (Product → Archive → Distribute) или приложение Transporter.
4. В App Store Connect: описание, скриншоты 6,7" и 6,5" iPhone, ссылка на политику конфиденциальности, «Конфиденциальность приложения» → «Данные не собираются», возрастной рейтинг.
5. Apple отклоняет приложения, которые выглядят как «просто сайт». Если откажут, сошлитесь на офлайн-лор, календарь недель и статус сервера.

## 5. Важно про Minecraft

В названии и описании не пишите, что приложение официальное. Используйте формулировку «фанатский сервер, не связан с Mojang и Microsoft» (она уже есть на сайте и в приложении). Не используйте логотип Minecraft.

## 6. Обновления

Поднимите `version:` в `app/pubspec.yaml` (например `1.0.1+2`, число после `+` должно расти), соберите заново и загрузите в консоли.

## Постоянная подпись APK (чтобы обновления ставились поверх)

Сейчас APK на GitHub подписывается отладочным ключом, и он новый в каждой сборке. Поэтому новую
версию нельзя поставить поверх старой: Android пишет «Приложение не установлено», и старую версию
приходится удалять. Чтобы подпись была постоянной, один раз сделайте ключ и положите его в секреты GitHub.

1. На ПК (нужна Java) в папке `app/android`:
   `keytool -genkeypair -v -keystore pax.jks -alias paxvanila -keyalg RSA -keysize 2048 -validity 10000`
   Придумайте пароль и запомните его. Файл `pax.jks` в git не попадёт (он в .gitignore). Сохраните его копию:
   если ключ потерять, обновления снова перестанут ставиться поверх.
2. Превратите ключ в текст. В PowerShell:
   `[Convert]::ToBase64String([IO.File]::ReadAllBytes("pax.jks")) | Set-Clipboard`
3. На GitHub: репозиторий → Settings → Secrets and variables → Actions → New repository secret:
   * `PAX_KEYSTORE_B64` — вставьте текст из буфера;
   * `PAX_KEYSTORE_PASSWORD` — пароль из шага 1.
4. Actions → Android APK → Run workflow. В журнале сборки появится «Постоянная подпись включена».
   После этой сборки старую версию нужно удалить один раз, дальше обновления ставятся поверх.

Номер версии (versionCode) растёт с каждой сборкой сам (номер запуска в Actions).
