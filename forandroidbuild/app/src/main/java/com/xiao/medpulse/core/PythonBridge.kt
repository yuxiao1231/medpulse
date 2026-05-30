package com.xiao.medpulse.core

import com.chaquo.python.Python
import org.json.JSONObject

data class CalculationResult(
    val success: Boolean,
    val result: String?,
    val error: String?
)

object PythonBridge {
    
    fun calculate(module: String, func: String, kwargs: Map<String, Any>): CalculationResult {
        if (!Python.isStarted()) {
            return CalculationResult(false, null, "Python Engine is not started.")
        }
        
        return try {
            val py = Python.getInstance()
            val bridge = py.getModule("bridge")
            
            // Serialize kwargs to JSON string to avoid Java Map iteration issues in Chaquopy
            val kwargsJson = JSONObject(kwargs).toString()
            
            val jsonResult = bridge.callAttr("wrap_call", module, func, kwargsJson).toString()
            val obj = JSONObject(jsonResult)
            
            if (obj.optBoolean("success", false)) {
                CalculationResult(true, obj.optString("result"), null)
            } else {
                CalculationResult(false, null, obj.optString("error") + "\n" + obj.optString("traceback"))
            }
        } catch (e: Exception) {
            CalculationResult(false, null, e.message)
        }
    }

    fun getImplementedScores(): CalculationResult {
        if (!Python.isStarted()) return CalculationResult(false, null, "Python Engine not started")
        return try {
            val py = Python.getInstance()
            val bridge = py.getModule("bridge")
            val jsonResult = bridge.callAttr("get_implemented_scores").toString()
            val obj = JSONObject(jsonResult)
            if (obj.optBoolean("success", false)) {
                CalculationResult(true, obj.optString("result"), null)
            } else {
                CalculationResult(false, null, obj.optString("error"))
            }
        } catch (e: Exception) {
            CalculationResult(false, null, e.message)
        }
    }

    fun getScoreSchema(scoreId: String): CalculationResult {
        if (!Python.isStarted()) return CalculationResult(false, null, "Python Engine not started")
        return try {
            val py = Python.getInstance()
            val bridge = py.getModule("bridge")
            val jsonResult = bridge.callAttr("get_score_schema", scoreId).toString()
            val obj = JSONObject(jsonResult)
            if (obj.optBoolean("success", false)) {
                CalculationResult(true, obj.optString("result"), null)
            } else {
                CalculationResult(false, null, obj.optString("error"))
            }
        } catch (e: Exception) {
            CalculationResult(false, null, e.message)
        }
    }

    fun getChecklists(): CalculationResult {
        if (!Python.isStarted()) return CalculationResult(false, null, "Python Engine not started")
        return try {
            val py = Python.getInstance()
            val bridge = py.getModule("bridge")
            val jsonResult = bridge.callAttr("get_checklists").toString()
            val obj = JSONObject(jsonResult)
            if (obj.optBoolean("success", false)) {
                CalculationResult(true, obj.optString("result"), null)
            } else {
                CalculationResult(false, null, obj.optString("error"))
            }
        } catch (e: Exception) {
            CalculationResult(false, null, e.message)
        }
    }

    fun calculateScoreWrap(scoreId: String, answersJson: String): CalculationResult {
        if (!Python.isStarted()) return CalculationResult(false, null, "Python Engine not started")
        return try {
            val py = Python.getInstance()
            val bridge = py.getModule("bridge")
            val jsonResult = bridge.callAttr("calculate_score_wrap", scoreId, answersJson).toString()
            val obj = JSONObject(jsonResult)
            if (obj.optBoolean("success", false)) {
                CalculationResult(true, obj.optString("result"), null)
            } else {
                CalculationResult(false, null, obj.optString("error"))
            }
        } catch (e: Exception) {
            CalculationResult(false, null, e.message)
        }
    }
}
