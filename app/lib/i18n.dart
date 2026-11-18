/// Язык интерфейса. Тексты контента лежат в assets/content(.en).json, здесь только подписи интерфейса.
library;

String lang = 'ru';
bool get isEn => lang == 'en';

/// t('русский', 'English') — выбрать подпись по текущему языку.
String t(String ru, String en) => isEn ? en : ru;

/// Суффикс папок ассетов: '' для русского, '_en' для английского.
String get assetSuffix => isEn ? '_en' : '';
