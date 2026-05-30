package com.xiao.medpulse.ui

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.core.view.WindowCompat
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items as lazyItems
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.LightMode
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.xiao.medpulse.core.PythonBridge
import com.xiao.medpulse.i18n.I18n
import com.xiao.medpulse.ui.theme.PocketIrTheme
import org.json.JSONObject
import org.json.JSONArray

private fun syncLocaleToPython(context: Context) {
    try {
        val prefs = context.getSharedPreferences("config", Context.MODE_PRIVATE)
        val forcedLang = prefs.getString("forced_language", "auto") ?: "auto"
        val activeTag = if (forcedLang == "auto") java.util.Locale.getDefault().toLanguageTag() else forcedLang
        
        if (Python.isStarted()) {
            val py = Python.getInstance()
            val bridge = py.getModule("bridge")
            bridge.callAttr("set_locale", activeTag)
        }
    } catch (e: Exception) {}
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)
        I18n.init(this)
        
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }
        syncLocaleToPython(this)

        setContent {
            MedPulseApp()
        }
    }
}

enum class CalculatorType(val id: String, val titleKey: String, val descKey: String) {
    ABG("abg", "abg_calc", "desc_abg"),
    ANION_GAP("anion_gap", "ag_calc", "desc_anion_gap"),
    WINTER("winter", "winter_calc", "desc_winter"),
    DELTA_GAP("delta_gap", "delta_gap_calc", "desc_delta_gap"),
    INFUSION("infusion", "infusion_calc", "desc_infusion"),
    DILUTION("dilution", "dilution_calc", "desc_dilution"),
    INSULIN("insulin", "insulin_calc", "desc_insulin"),
    ANTIBIOTIC("antibiotic", "antibiotic_calc", "desc_antibiotic"),
    BURN("burn", "burn_calc", "desc_burn"),
    PEDIATRICS("pediatrics", "pediatrics_calc", "desc_pediatrics"),
    QSOFA("qsofa", "qsofa_calc", "desc_qsofa"),
    GCS("gcs", "gcs_calc", "desc_gcs"),
    CHECKLISTS("checklists", "checklists_tab", "desc_checklists")
}

data class ToolItem(val id: String, val type: String, val name: String)

private fun getAvailableTools(): List<ToolItem> {
    val tools = mutableListOf<ToolItem>()
    for (c in CalculatorType.values()) {
        tools.add(ToolItem(c.id, "NATIVE", I18n.t(c.titleKey)))
    }
    return tools
}

private data class LangOption(val displayName: String, val tag: String)

private fun loadLangOptions(context: Context): List<LangOption> {
    val fromAssets = runCatching {
        context.assets.list("locales")
            ?.filter { it.endsWith(".json") }
            ?.mapNotNull { filename ->
                val base = filename.removeSuffix(".json")
                val tag = base.replace("_", "-")
                val displayName = runCatching {
                    val text = context.assets.open("locales/$filename")
                        .bufferedReader().use { it.readText() }
                    JSONObject(text).optString("lang_name", tag).ifBlank { tag }
                }.getOrDefault(tag)
                LangOption(displayName, tag)
            }
            ?.sortedBy { it.tag }
    }.getOrNull().orEmpty()
    return listOf(LangOption(I18n.t("lang_auto"), "auto")) + fromAssets
}

@Composable
private fun LanguageDialog(onDismiss: () -> Unit, onApply: (tag: String) -> Unit) {
    val context = LocalContext.current
    val currentTag = remember { context.getSharedPreferences("config", Context.MODE_PRIVATE).getString("forced_language", "auto") ?: "auto" }
    val options = remember { loadLangOptions(context) }
    var selected by remember { mutableStateOf(currentTag) }
    val haptic = LocalHapticFeedback.current

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(I18n.t("dialog_lang_title")) },
        text = {
            Column(modifier = Modifier.selectableGroup()) {
                options.forEach { option ->
                    Row(
                        modifier = Modifier.fillMaxWidth().height(48.dp).selectable(
                            selected = (option.tag == selected),
                            onClick = { 
                                haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                                selected = option.tag 
                            },
                            role = Role.RadioButton
                        ),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        RadioButton(selected = (option.tag == selected), onClick = null)
                        Text(text = option.displayName, style = MaterialTheme.typography.bodyLarge, modifier = Modifier.padding(start = 12.dp))
                    }
                }
            }
        },
        confirmButton = { Button(onClick = { 
            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
            onApply(selected) 
        }) { Text(I18n.t("btn_apply")) } },
        dismissButton = { TextButton(onClick = {
            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
            onDismiss()
        }) { Text(I18n.t("btn_cancel")) } }
    )
}

@Composable
private fun LayoutManagerDialog(allTools: List<ToolItem>, onDismiss: () -> Unit, onApply: (Set<String>) -> Unit) {
    val context = LocalContext.current
    val prefs = context.getSharedPreferences("layout", Context.MODE_PRIVATE)
    val haptic = LocalHapticFeedback.current
    
    // Default show all if empty
    var selectedIds by remember { 
        mutableStateOf(
            (prefs.getStringSet("active_tools", allTools.map { it.id }.toSet()) ?: allTools.map { it.id }.toSet())
                .map { it.lowercase() }.toSet()
        )
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(I18n.t("desc_settings")) },
        text = {
            LazyColumn {
                lazyItems(allTools) { tool ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable {
                                haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                                val newSet = selectedIds.toMutableSet()
                                if (newSet.contains(tool.id)) newSet.remove(tool.id) else newSet.add(tool.id)
                                selectedIds = newSet
                            }
                            .padding(vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Checkbox(
                            checked = selectedIds.contains(tool.id),
                            onCheckedChange = null
                        )
                        Text(text = tool.name, modifier = Modifier.padding(start = 12.dp))
                    }
                }
            }
        },
        confirmButton = { 
            Button(onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                prefs.edit().putStringSet("active_tools", selectedIds).apply()
                onApply(selectedIds)
            }) { Text(I18n.t("btn_apply")) } 
        },
        dismissButton = { TextButton(onClick = {
            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
            onDismiss()
        }) { Text(I18n.t("btn_cancel")) } }
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MedPulseApp() {
    val navController = rememberNavController()
    val context = LocalContext.current
    val haptic = LocalHapticFeedback.current
    val configPrefs = remember { context.getSharedPreferences("config", Context.MODE_PRIVATE) }
    var isDarkMode by remember { mutableStateOf(configPrefs.getBoolean("is_dark_mode", false)) }
    var showLangDialog by rememberSaveable { mutableStateOf(false) }
    var showLayoutDialog by rememberSaveable { mutableStateOf(false) }
    var langVersion by remember { mutableIntStateOf(0) }
    var layoutVersion by remember { mutableIntStateOf(0) }
    
    val allTools = remember(langVersion) { getAvailableTools() }

    PocketIrTheme(darkTheme = isDarkMode) {
        if (showLangDialog) {
            LanguageDialog(
                onDismiss = { showLangDialog = false },
                onApply = { tag ->
                    configPrefs.edit().putString("forced_language", tag).apply()
                    I18n.init(context)
                    syncLocaleToPython(context)
                    langVersion++
                    showLangDialog = false
                }
            )
        }
        if (showLayoutDialog) {
            LayoutManagerDialog(
                allTools = allTools,
                onDismiss = { showLayoutDialog = false },
                onApply = { 
                    layoutVersion++
                    showLayoutDialog = false
                }
            )
        }
        
        key(langVersion, layoutVersion) {
            Scaffold(
                topBar = {
                    TopAppBar(
                        title = { Text(I18n.t("app_name")) },
                        actions = {
                            IconButton(onClick = { 
                                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                showLayoutDialog = true 
                            }) {
                                Icon(Icons.Default.Settings, contentDescription = "Layout")
                            }
                            IconButton(onClick = { 
                                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                showLangDialog = true 
                            }) {
                                Icon(Icons.Default.Language, contentDescription = "Language")
                            }
                            IconButton(onClick = { 
                                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                val newMode = !isDarkMode
                                isDarkMode = newMode
                                configPrefs.edit().putBoolean("is_dark_mode", newMode).apply()
                            }) {
                                Icon(if (isDarkMode) Icons.Default.LightMode else Icons.Default.DarkMode, contentDescription = "Theme")
                            }
                        }
                    )
                }
            ) { innerPadding ->
                NavHost(navController = navController, startDestination = "home", modifier = Modifier.padding(innerPadding).imePadding()) {
                    composable("home") {
                        val activeIdsRaw = context.getSharedPreferences("layout", Context.MODE_PRIVATE).getStringSet("active_tools", allTools.map { it.id }.toSet()) ?: allTools.map { it.id }.toSet()
                        val activeIds = activeIdsRaw.map { it.lowercase() }.toSet()
                        val activeTools = allTools.filter { activeIds.contains(it.id) }
                        
                        HomeScreen(activeTools, onNavigate = { tool -> 
                            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                            navController.navigate("tool/${tool.id}") 
                        })
                    }
                    composable("tool/{id}") { backStackEntry ->
                        val id = backStackEntry.arguments?.getString("id") ?: ""
                        val tool = CalculatorType.values().find { it.id == id }
                        
                        Column(modifier = Modifier.fillMaxSize()) {
                            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(8.dp)) {
                                IconButton(onClick = { 
                                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                    navController.popBackStack() 
                                }) {
                                    Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                                }
                                Text(text = if (tool != null) I18n.t(tool.titleKey) else "", style = MaterialTheme.typography.titleLarge)
                            }
                            if (tool != null) {
                                val desc = I18n.t(tool.descKey)
                                if (desc.isNotEmpty()) {
                                    Card(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(horizontal = 16.dp, vertical = 8.dp),
                                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                                    ) {
                                        Text(
                                            text = desc,
                                            modifier = Modifier.padding(12.dp),
                                            style = MaterialTheme.typography.bodyMedium,
                                            color = MaterialTheme.colorScheme.onSurfaceVariant
                                        )
                                    }
                                }
                                
                                Box(modifier = Modifier.fillMaxSize()) {
                                    when (tool) {
                                        CalculatorType.ABG -> AbgScreen()
                                        CalculatorType.ANION_GAP -> AnionGapScreen()
                                        CalculatorType.WINTER -> WinterScreen()
                                        CalculatorType.DELTA_GAP -> DeltaGapScreen()
                                        CalculatorType.INFUSION -> InfusionScreen()
                                        CalculatorType.DILUTION -> DilutionScreen()
                                        CalculatorType.INSULIN -> InsulinScreen()
                                        CalculatorType.ANTIBIOTIC -> AntibioticScreen()
                                        CalculatorType.BURN -> BurnScreen()
                                        CalculatorType.PEDIATRICS -> PediatricsScreen()
                                        CalculatorType.QSOFA -> ScoreScreen("qsofa")
                                        CalculatorType.GCS -> ScoreScreen("gcs")
                                        CalculatorType.CHECKLISTS -> ChecklistSelectionScreen(
                                            onNavigateToChecklist = { checklistId ->
                                                navController.navigate("checklist/$checklistId")
                                            }
                                        )
                                    }
                                }
                            }
                        }
                    }
                    composable("checklist/{checklistId}") { backStackEntry ->
                        val checklistId = backStackEntry.arguments?.getString("checklistId") ?: ""
                        var checklistTitle by remember { mutableStateOf("") }
                        
                        LaunchedEffect(checklistId) {
                            val res = PythonBridge.getChecklists()
                            if (res.success && res.result != null) {
                                try {
                                    val arr = JSONArray(res.result)
                                    for (i in 0 until arr.length()) {
                                        val obj = arr.getJSONObject(i)
                                        if (obj.getString("id") == checklistId) {
                                            checklistTitle = I18n.t("chk_${checklistId}_title", obj.getString("title"))
                                            break
                                        }
                                    }
                                } catch (e: Exception) {}
                            }
                        }

                        Column(modifier = Modifier.fillMaxSize()) {
                            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(8.dp)) {
                                IconButton(onClick = { 
                                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                    navController.popBackStack() 
                                }) {
                                    Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                                }
                                Text(text = checklistTitle, style = MaterialTheme.typography.titleLarge)
                            }
                            ChecklistScreen(checklistId)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun HomeScreen(tools: List<ToolItem>, onNavigate: (ToolItem) -> Unit) {
    LazyVerticalGrid(
        columns = GridCells.Fixed(2),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        items(tools) { tool ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(1f)
                    .clickable { onNavigate(tool) },
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
            ) {
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier.fillMaxSize()
                ) {
                    Text(text = tool.name, style = MaterialTheme.typography.titleMedium)
                }
            }
        }
    }
}

@Composable
fun ScoreScreen(scoreId: String) {
    var schemaObj by remember { mutableStateOf<JSONObject?>(null) }
    var answers by remember { mutableStateOf(mapOf<String, Any>()) }
    var resultText by remember { mutableStateOf("") }
    val haptic = LocalHapticFeedback.current
    
    LaunchedEffect(scoreId) {
        val res = PythonBridge.getScoreSchema(scoreId)
        if (res.success && res.result != null) {
            try {
                schemaObj = JSONObject(res.result)
            } catch (e: Exception) {}
        }
    }

    if (schemaObj == null) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        return
    }
    
    val itemsArray = schemaObj!!.optJSONArray("items") ?: JSONArray()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        for (i in 0 until itemsArray.length()) {
            val item = itemsArray.getJSONObject(i)
            val id = item.getString("id")
            val label = item.getString("label")
            val type = item.getString("type")
            
            val labelKey = "${scoreId}_${id}"
            val labelT = I18n.t(labelKey)
            val itemLabel = if (labelT != labelKey) labelT else label

            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = itemLabel, fontWeight = FontWeight.Bold, modifier = Modifier.padding(bottom = 8.dp))
                    
                    if (type == "boolean") {
                        val isChecked = answers[id] as? Boolean ?: false
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                                    val newAnswers = answers.toMutableMap()
                                    newAnswers[id] = !isChecked
                                    answers = newAnswers
                                }
                        ) {
                            Checkbox(checked = isChecked, onCheckedChange = null)
                            Text(I18n.t("yes"), modifier = Modifier.padding(start = 8.dp))
                        }
                    } else if (type == "choice") {
                        val options = item.optJSONArray("options") ?: JSONArray()
                        val selectedOpt = answers[id] as? String
                        
                        Column(modifier = Modifier.selectableGroup()) {
                            for (j in 0 until options.length()) {
                                val opt = options.getJSONObject(j)
                                val optId = opt.getString("id")
                                val optLabel = opt.getString("label")
                                
                                val optKey = "${scoreId}_${id}_${optId}"
                                val optLabelT = I18n.t(optKey)
                                val optDisplay = if (optLabelT != optKey) optLabelT else optLabel

                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .height(48.dp)
                                        .selectable(
                                            selected = (optId == selectedOpt),
                                            onClick = {
                                                haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                                                val newAnswers = answers.toMutableMap()
                                                newAnswers[id] = optId
                                                answers = newAnswers
                                            },
                                            role = Role.RadioButton
                                        ),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    RadioButton(selected = (optId == selectedOpt), onClick = null)
                                    Text(text = optDisplay, modifier = Modifier.padding(start = 12.dp))
                                }
                            }
                        }
                    }
                }
            }
        }
        
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val jsonAnswers = JSONObject(answers as Map<*, *>).toString()
                val res = PythonBridge.calculateScoreWrap(scoreId, jsonAnswers)
                if (res.success && res.result != null) {
                    resultText = res.result!!
                } else {
                    resultText = "${I18n.t("calc_error")}: ${res.error}"
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calculate"))
        }
        
        if (resultText.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
                Text(text = resultText, modifier = Modifier.padding(16.dp), fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onPrimaryContainer)
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
    }
}

@Composable
fun DilutionScreen() {
    var mg by remember { mutableStateOf("") }
    var ml by remember { mutableStateOf("") }
    var resultText by remember { mutableStateOf("") }
    val haptic = LocalHapticFeedback.current

    Column(modifier = Modifier.padding(16.dp).fillMaxSize().verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        OutlinedTextField(
            value = mg,
            onValueChange = { mg = it },
            label = { Text(I18n.t("input_drug_amount")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = ml,
            onValueChange = { ml = it },
            label = { Text(I18n.t("input_diluent_vol")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val mgVal = mg.toFloatOrNull()
                val mlVal = ml.toFloatOrNull()
                if (mgVal != null && mlVal != null) {
                    val res = PythonBridge.calculate("drugs", "dilute_powder", mapOf("amount_mg" to mgVal, "volume_ml" to mlVal))
                    resultText = if (res.success) res.result ?: "" else res.error ?: "Error"
                } else {
                    resultText = I18n.t("error_valid_number")
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calculate"))
        }
        
        if (resultText.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = resultText, modifier = Modifier.padding(16.dp))
            }
        }
    }
}

@Composable
fun InsulinScreen() {
    var weight by remember { mutableStateOf("") }
    var resultTextTdd by remember { mutableStateOf("") }
    
    var conc by remember { mutableStateOf("") }
    var vol by remember { mutableStateOf("") }
    var ratio by remember { mutableStateOf("4") }
    var resultTextGi by remember { mutableStateOf("") }
    
    val haptic = LocalHapticFeedback.current

    Column(modifier = Modifier.padding(16.dp).fillMaxSize().verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        
        Text(text = I18n.t("insulin_calc"), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        
        OutlinedTextField(
            value = weight,
            onValueChange = { weight = it },
            label = { Text(I18n.t("input_weight")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val weightVal = weight.toFloatOrNull()
                if (weightVal != null) {
                    val res = PythonBridge.calculate("drugs", "insulin_tdd", mapOf("weight_kg" to weightVal))
                    resultTextTdd = if (res.success) res.result ?: "" else res.error ?: "Error"
                } else {
                    resultTextTdd = I18n.t("error_valid_number")
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calc_tdd"))
        }
        
        if (resultTextTdd.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = resultTextTdd, modifier = Modifier.padding(16.dp))
            }
        }
        
        HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
        
        Text(text = I18n.t("glucose_insulin_calc"), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
        
        OutlinedTextField(
            value = conc,
            onValueChange = { conc = it },
            label = { Text(I18n.t("input_glucose_conc")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = vol,
            onValueChange = { vol = it },
            label = { Text(I18n.t("input_glucose_vol")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = ratio,
            onValueChange = { ratio = it },
            label = { Text(I18n.t("input_insulin_ratio")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val c = conc.toFloatOrNull()
                val v = vol.toFloatOrNull()
                val r = ratio.toFloatOrNull()
                if (c != null && v != null && r != null) {
                    val res = PythonBridge.calculate("drugs", "glucose_insulin", mapOf("concentration_pct" to c, "volume_ml" to v, "ratio_g_per_u" to r))
                    resultTextGi = if (res.success) res.result ?: "" else res.error ?: "Error"
                } else {
                    resultTextGi = I18n.t("error_valid_number")
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calc_glucose_insulin"))
        }
        
        if (resultTextGi.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = resultTextGi, modifier = Modifier.padding(16.dp))
            }
        }
    }
}

@Composable
fun AntibioticScreen() {
    var weight by remember { mutableStateOf("") }
    var dose by remember { mutableStateOf("") }
    var resultText by remember { mutableStateOf("") }
    val haptic = LocalHapticFeedback.current

    Column(modifier = Modifier.padding(16.dp).fillMaxSize().verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        OutlinedTextField(
            value = weight,
            onValueChange = { weight = it },
            label = { Text(I18n.t("input_weight")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = dose,
            onValueChange = { dose = it },
            label = { Text(I18n.t("input_dose_req")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val weightVal = weight.toFloatOrNull()
                val doseVal = dose.toFloatOrNull()
                if (weightVal != null && doseVal != null) {
                    val res = PythonBridge.calculate("drugs", "antibiotic_dose", mapOf("weight_kg" to weightVal, "dose_mg_per_kg" to doseVal))
                    resultText = if (res.success) res.result ?: "" else res.error ?: "Error"
                } else {
                    resultText = I18n.t("error_valid_number")
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calculate"))
        }
        
        if (resultText.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = resultText, modifier = Modifier.padding(16.dp))
            }
        }
    }
}

@Composable
fun BurnScreen() {
    var weight by remember { mutableStateOf("") }
    var tbsa by remember { mutableStateOf("") }
    var resultText by remember { mutableStateOf("") }
    val haptic = LocalHapticFeedback.current

    Column(modifier = Modifier.padding(16.dp).fillMaxSize(), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        OutlinedTextField(
            value = weight,
            onValueChange = { weight = it },
            label = { Text(I18n.t("input_weight")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = tbsa,
            onValueChange = { tbsa = it },
            label = { Text(I18n.t("input_tbsa")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val weightVal = weight.toFloatOrNull()
                val tbsaVal = tbsa.toFloatOrNull()
                if (weightVal != null && tbsaVal != null) {
                    val res = PythonBridge.calculate("burns", "parkland_formula", mapOf("weight_kg" to weightVal, "tbsa_percent" to tbsaVal))
                    resultText = if (res.success) res.result ?: "" else res.error ?: "Error"
                } else {
                    resultText = I18n.t("error_valid_number")
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calculate"))
        }
        
        if (resultText.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = resultText, modifier = Modifier.padding(16.dp))
            }
        }
    }
}

@Composable
fun ChecklistSelectionScreen(onNavigateToChecklist: (String) -> Unit) {
    var checklists by remember { mutableStateOf<List<JSONObject>>(emptyList()) }
    val haptic = LocalHapticFeedback.current

    LaunchedEffect(Unit) {
        val res = PythonBridge.getChecklists()
        if (res.success && res.result != null) {
            try {
                val arr = JSONArray(res.result)
                val list = mutableListOf<JSONObject>()
                for (i in 0 until arr.length()) {
                    list.add(arr.getJSONObject(i))
                }
                checklists = list
            } catch (e: Exception) {}
        }
    }

    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        lazyItems(checklists) { item ->
            val id = item.getString("id")
            val title = item.getString("title")
            val titleT = I18n.t("chk_${id}_title", title)
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable {
                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                        onNavigateToChecklist(id)
                    },
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Box(
                    modifier = Modifier.padding(16.dp).fillMaxWidth(),
                    contentAlignment = Alignment.CenterStart
                ) {
                    Text(text = titleT, style = MaterialTheme.typography.titleMedium)
                }
            }
        }
    }
}

@Composable
fun ChecklistScreen(checklistId: String) {
    var checklistObj by remember { mutableStateOf<JSONObject?>(null) }
    var checkedStates by remember { mutableStateOf(mapOf<Int, Boolean>()) }
    val haptic = LocalHapticFeedback.current

    LaunchedEffect(checklistId) {
        val res = PythonBridge.getChecklists()
        if (res.success && res.result != null) {
            try {
                val arr = JSONArray(res.result)
                for (i in 0 until arr.length()) {
                    val obj = arr.getJSONObject(i)
                    if (obj.getString("id") == checklistId) {
                        checklistObj = obj
                        break
                    }
                }
            } catch (e: Exception) {}
        }
    }

    if (checklistObj == null) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        return
    }

    val checksArray = checklistObj!!.optJSONArray("checks") ?: JSONArray()
    val note = I18n.t("checklist_note")

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer)
        ) {
            Text(
                text = note,
                modifier = Modifier.padding(12.dp),
                color = MaterialTheme.colorScheme.onTertiaryContainer,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold
            )
        }

        for (i in 0 until checksArray.length()) {
            val checkText = checksArray.getString(i)
            val isChecked = checkedStates[i] ?: false
            val itemKey = "chk_${checklistId}_item_${i}"
            val itemT = I18n.t(itemKey)
            val displayCheckText = if (itemT != itemKey) itemT else checkText

            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable {
                        haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                        val newStates = checkedStates.toMutableMap()
                        newStates[i] = !isChecked
                        checkedStates = newStates
                    },
                elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
            ) {
                Row(
                    modifier = Modifier.padding(16.dp).fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Checkbox(
                        checked = isChecked,
                        onCheckedChange = null
                    )
                    Text(
                        text = displayCheckText,
                        modifier = Modifier.padding(start = 12.dp),
                        style = MaterialTheme.typography.bodyLarge
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
    }
}

@Composable
fun AbgScreen() {
    var ph by remember { mutableStateOf("") }
    var pco2 by remember { mutableStateOf("") }
    var hco3 by remember { mutableStateOf("") }
    var resultText by remember { mutableStateOf("") }
    val haptic = LocalHapticFeedback.current

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        OutlinedTextField(
            value = ph, onValueChange = { ph = it },
            label = { Text(I18n.t("input_ph")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = pco2, onValueChange = { pco2 = it },
            label = { Text(I18n.t("input_pco2")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = hco3, onValueChange = { hco3 = it },
            label = { Text(I18n.t("input_hco3")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val phVal = ph.toFloatOrNull()
                val pco2Val = pco2.toFloatOrNull()
                val hco3Val = hco3.toFloatOrNull()
                if (phVal != null && pco2Val != null && hco3Val != null) {
                    val res = PythonBridge.calculate("abg", "analyze_abg", mapOf("ph" to phVal, "pco2" to pco2Val, "hco3" to hco3Val))
                    resultText = if (res.success) res.result ?: "" else res.error ?: "Error"
                } else {
                    resultText = I18n.t("error_valid_number")
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calculate"))
        }
        
        if (resultText.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = resultText, modifier = Modifier.padding(16.dp))
            }
        }
    }
}

@Composable
fun AnionGapScreen() {
    var na by remember { mutableStateOf("") }
    var cl by remember { mutableStateOf("") }
    var hco3 by remember { mutableStateOf("") }
    var albumin by remember { mutableStateOf("") }
    var resultText by remember { mutableStateOf("") }
    val haptic = LocalHapticFeedback.current

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        OutlinedTextField(
            value = na, onValueChange = { na = it },
            label = { Text(I18n.t("input_na")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = cl, onValueChange = { cl = it },
            label = { Text(I18n.t("input_cl")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = hco3, onValueChange = { hco3 = it },
            label = { Text(I18n.t("input_hco3")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = albumin, onValueChange = { albumin = it },
            label = { Text(I18n.t("input_albumin")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val naVal = na.toFloatOrNull()
                val clVal = cl.toFloatOrNull()
                val hco3Val = hco3.toFloatOrNull()
                val albuminVal = albumin.toFloatOrNull()
                
                if (naVal != null && clVal != null && hco3Val != null) {
                    val map = mutableMapOf<String, Any>("na" to naVal, "cl" to clVal, "hco3" to hco3Val)
                    if (albuminVal != null) map["albumin"] = albuminVal
                    val res = PythonBridge.calculate("electrolytes", "anion_gap", map)
                    resultText = if (res.success) res.result ?: "" else res.error ?: "Error"
                } else {
                    resultText = I18n.t("error_required_number")
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calculate"))
        }
        
        if (resultText.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = resultText, modifier = Modifier.padding(16.dp))
            }
        }
    }
}

@Composable
fun WinterScreen() {
    var hco3 by remember { mutableStateOf("") }
    var pco2 by remember { mutableStateOf("") }
    var resultText by remember { mutableStateOf("") }
    val haptic = LocalHapticFeedback.current

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        OutlinedTextField(
            value = hco3, onValueChange = { hco3 = it },
            label = { Text(I18n.t("input_hco3")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = pco2, onValueChange = { pco2 = it },
            label = { Text(I18n.t("input_actual_pco2")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val hco3Val = hco3.toFloatOrNull()
                val pco2Val = pco2.toFloatOrNull()
                
                if (hco3Val != null) {
                    val map = mutableMapOf<String, Any>("hco3" to hco3Val)
                    if (pco2Val != null) map["actual_pco2"] = pco2Val
                    val res = PythonBridge.calculate("electrolytes", "winter_expected_pco2", map)
                    resultText = if (res.success) res.result ?: "" else res.error ?: "Error"
                } else {
                    resultText = I18n.t("error_input_hco3")
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calculate"))
        }
        
        if (resultText.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = resultText, modifier = Modifier.padding(16.dp))
            }
        }
    }
}

@Composable
fun DeltaGapScreen() {
    var ag by remember { mutableStateOf("") }
    var hco3 by remember { mutableStateOf("") }
    var resultText by remember { mutableStateOf("") }
    val haptic = LocalHapticFeedback.current

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        OutlinedTextField(
            value = ag, onValueChange = { ag = it },
            label = { Text(I18n.t("input_ag")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = hco3, onValueChange = { hco3 = it },
            label = { Text(I18n.t("input_hco3")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val agVal = ag.toFloatOrNull()
                val hco3Val = hco3.toFloatOrNull()
                
                if (agVal != null && hco3Val != null) {
                    val res = PythonBridge.calculate("electrolytes", "delta_gap", mapOf("ag_value" to agVal, "hco3" to hco3Val))
                    resultText = if (res.success) res.result ?: "" else res.error ?: "Error"
                } else {
                    resultText = I18n.t("error_valid_number")
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calculate"))
        }
        
        if (resultText.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = resultText, modifier = Modifier.padding(16.dp))
            }
        }
    }
}

@Composable
fun InfusionScreen() {
    var isToVolume by remember { mutableStateOf(true) }
    
    var weight by remember { mutableStateOf("") }
    var dose by remember { mutableStateOf("") }
    var drug by remember { mutableStateOf("") }
    var volume by remember { mutableStateOf("") }
    var rate by remember { mutableStateOf("") }
    
    var resultText by remember { mutableStateOf("") }
    val haptic = LocalHapticFeedback.current

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(I18n.t("mode"), style = MaterialTheme.typography.bodyLarge)
            Spacer(modifier = Modifier.width(8.dp))
            Button(onClick = { 
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                isToVolume = true 
            }, colors = ButtonDefaults.buttonColors(containerColor = if (isToVolume) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.secondary)) {
                Text(I18n.t("mode_dose_to_rate"))
            }
            Spacer(modifier = Modifier.width(8.dp))
            Button(onClick = { 
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                isToVolume = false 
            }, colors = ButtonDefaults.buttonColors(containerColor = if (!isToVolume) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.secondary)) {
                Text(I18n.t("mode_rate_to_dose"))
            }
        }
        
        OutlinedTextField(
            value = weight, onValueChange = { weight = it },
            label = { Text(I18n.t("input_weight")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = drug, onValueChange = { drug = it },
            label = { Text(I18n.t("input_drug_total")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = volume, onValueChange = { volume = it },
            label = { Text(I18n.t("input_volume_total")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        
        if (isToVolume) {
            OutlinedTextField(
                value = dose, onValueChange = { dose = it },
                label = { Text(I18n.t("input_target_dose")) },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                modifier = Modifier.fillMaxWidth()
            )
        } else {
            OutlinedTextField(
                value = rate, onValueChange = { rate = it },
                label = { Text(I18n.t("input_current_rate")) },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                modifier = Modifier.fillMaxWidth()
            )
        }
        
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val w = weight.toFloatOrNull()
                val d = drug.toFloatOrNull()
                val v = volume.toFloatOrNull()
                
                if (w != null && d != null && v != null) {
                    if (isToVolume) {
                        val doseVal = dose.toFloatOrNull()
                        if (doseVal != null) {
                            val res = PythonBridge.calculate("infusion", "infusion_rate_from_amount", 
                                mapOf("dose_mcg_per_kg_min" to doseVal, "weight_kg" to w, "drug_mg" to d, "volume_ml" to v))
                            resultText = if (res.success) res.result ?: "" else res.error ?: "Error"
                        } else {
                            resultText = I18n.t("error_target_dose")
                        }
                    } else {
                        val rateVal = rate.toFloatOrNull()
                        if (rateVal != null) {
                            val res = PythonBridge.calculate("infusion", "infusion_dose_from_amount", 
                                mapOf("rate_ml_per_hour" to rateVal, "weight_kg" to w, "drug_mg" to d, "volume_ml" to v))
                            resultText = if (res.success) res.result ?: "" else res.error ?: "Error"
                        } else {
                            resultText = I18n.t("error_current_rate")
                        }
                    }
                } else {
                    resultText = I18n.t("error_weight_drug_volume")
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calculate"))
        }
        
        if (resultText.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = resultText, modifier = Modifier.padding(16.dp))
            }
        }
    }
}

@Composable
fun PediatricsScreen() {
    var weight by remember { mutableStateOf("") }
    var height by remember { mutableStateOf("") }
    var bsaResultText by remember { mutableStateOf("") }
    var fluidResultText by remember { mutableStateOf("") }
    val haptic = LocalHapticFeedback.current

    Column(modifier = Modifier.fillMaxSize().padding(16.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        OutlinedTextField(
            value = weight, onValueChange = { weight = it },
            label = { Text(I18n.t("input_weight")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        OutlinedTextField(
            value = height, onValueChange = { height = it },
            label = { Text(I18n.t("input_height")) },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        
        Button(
            onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                val w = weight.toFloatOrNull()
                val h = height.toFloatOrNull()
                
                if (w != null) {
                    val res421 = PythonBridge.calculate("pediatrics", "maintenance_fluid_421", mapOf("weight_kg" to w))
                    fluidResultText = if (res421.success) res421.result ?: "" else res421.error ?: "Error"
                    
                    if (h != null) {
                        val resBsa = PythonBridge.calculate("pediatrics", "mosteller_bsa", mapOf("weight_kg" to w, "height_cm" to h))
                        bsaResultText = if (resBsa.success) resBsa.result ?: "" else resBsa.error ?: "Error"
                    } else {
                        bsaResultText = ""
                    }
                } else {
                    fluidResultText = I18n.t("error_ped_weight")
                    bsaResultText = ""
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(I18n.t("btn_calculate"))
        }
        
        if (bsaResultText.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = bsaResultText, modifier = Modifier.padding(16.dp))
            }
        }
        
        if (fluidResultText.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                Text(text = fluidResultText, modifier = Modifier.padding(16.dp))
            }
        }
    }
}
