plugins {
    id("com.android.application")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.paxvanila.paxvanila"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        // TODO: Specify your own unique Application ID (https://developer.android.com/studio/build/application-id.html).
        applicationId = "com.paxvanila.paxvanila"
        // You can update the following values to match your application needs.
        // For more information, see: https://flutter.dev/to/review-gradle-config.
        minSdk = flutter.minSdkVersion
        targetSdk = flutter.targetSdkVersion
        // Uses the version code from pubspec.yaml. When using split APKs, 1000 * ABI_VERSION
        // is added automatically by Flutter. (https://developer.android.com/studio/build/configure-apk-splits#configure-APK-versions)
        // You can force using the value of versionCode by specifying the `-P force-version-code-ignoring-abi=true`
        // flag during build.
        versionCode = flutter.versionCode
        versionName = flutter.versionName
    }

    // Постоянная подпись: если заданы переменные PAX_KEYSTORE* (секреты GitHub, см. app/RELEASE.md),
    // APK подписывается одним и тем же ключом и обновления ставятся поверх старой версии.
    // Без них — отладочная подпись (ключ меняется от сборки к сборке).
    val paxKeystore = System.getenv("PAX_KEYSTORE")
    val paxSigned = paxKeystore != null && file(paxKeystore).exists()
    signingConfigs {
        if (paxSigned) {
            create("pax") {
                storeFile = file(paxKeystore!!)
                storePassword = System.getenv("PAX_KEYSTORE_PASSWORD")
                keyAlias = System.getenv("PAX_KEY_ALIAS") ?: "paxvanila"
                keyPassword = System.getenv("PAX_KEY_PASSWORD") ?: System.getenv("PAX_KEYSTORE_PASSWORD")
            }
        }
    }

    buildTypes {
        release {
            signingConfig = if (paxSigned) signingConfigs.getByName("pax") else signingConfigs.getByName("debug")
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}
