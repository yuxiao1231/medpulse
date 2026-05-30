package com.xiao.medpulse.i18n

import android.content.Context
import org.json.JSONObject
import java.io.File
import java.util.Locale

object I18n {
    private const val FALLBACK_LANG = "en"

    private var fallbackData = JSONObject()
    private var langData = JSONObject()

    fun init(context: Context) {
        val prefs = context.getSharedPreferences("config", Context.MODE_PRIVATE)
        val forcedLang = prefs.getString("forced_language", "auto") ?: "auto"
        val activeTag = if (forcedLang == "auto") Locale.getDefault().toLanguageTag() else forcedLang

        fallbackData = loadLangJson(context, FALLBACK_LANG)
        langData = loadLangJson(context, activeTag)

        if (langData.length() == 0 && activeTag.contains("-")) {
            val baseTag = activeTag.substringBefore("-")
            if (baseTag != FALLBACK_LANG) {
                langData = loadLangJson(context, baseTag)
            }
        }
    }

    fun t(key: String, vararg args: Any?): String {
        val raw = when {
            langData.has(key) -> langData.getString(key)
            fallbackData.has(key) -> fallbackData.getString(key)
            else -> key
        }
        return runCatching {
            if (args.isEmpty()) raw else String.format(Locale.getDefault(), raw, *args)
        }.getOrDefault(raw)
    }

    private fun loadLangJson(context: Context, langTag: String): JSONObject {
        val assetPath = "locales/${langTag.replace("-", "_")}.json"
        val overrideFile = File(context.getExternalFilesDir(null), assetPath)

        if (overrideFile.exists()) {
            return runCatching { JSONObject(overrideFile.readText()) }.getOrDefault(JSONObject())
        }

        return runCatching {
            val text = context.assets.open(assetPath).bufferedReader().use { it.readText() }
            JSONObject(text)
        }.getOrDefault(JSONObject())
    }
}
