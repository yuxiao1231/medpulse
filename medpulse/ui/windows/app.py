"""Modern Tkinter desktop shell for MedPulse with Sidebar navigation."""

import tkinter as tk
from tkinter import messagebox, ttk
import json
import sys
import os

from medpulse.core.calculators import (
    analyze_abg,
    anion_gap,
    concentration_from_amount,
    infusion_dose_result,
    infusion_rate_result,
    winter_expected_pco2,
)
from medpulse.core.calculators.electrolytes import delta_gap
from medpulse.core.calculators.pediatrics import maintenance_fluid_421, mosteller_bsa
from medpulse.core.calculators.drugs import dilute_powder, glucose_insulin, insulin_tdd, antibiotic_dose
from medpulse.core.calculators.burns import parkland_formula
from medpulse.core.exceptions import ValidationError
from medpulse.core.scores import ScoreService
from medpulse.core.resources import load_json, list_json_files
from medpulse.i18n import Translator, set_global_locale
from medpulse.ui.adapter import ResultFormatter
from medpulse.ui.windows.widgets import CustomCheckbox


class MedPulseTkApp(tk.Tk):
    def __init__(self, locale=None):
        super().__init__()
        
        self.settings_file = os.path.join(
            os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)),
            "settings.json"
        )
        
        self.preferences = {
            "locale": locale or "en",
            "anion_gap": True,
            "winter": True,
            "infusion": True,
            "abg": True,
            "delta_gap": True,
            "pediatrics": True,
            "qsofa": True,
            "gcs": True,
            "checklists": True,
            "dilution": True,
            "insulin": True,
            "antibiotic": True,
            "burn": True,
            "settings": True
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    self.preferences.update(json.load(f))
        except Exception:
            pass

        active_locale = self.preferences.get("locale", "en")
        self.translator = Translator(active_locale)
        set_global_locale(active_locale)
        self.score_service = ScoreService()
        self.formatter = ResultFormatter()
        self._gcs_definition = self.score_service.load_definition("gcs")
        self._gcs_option_maps = {}
        self._image_cache = []

        self.title(self.translator.t("app_title", "MedPulse"))
        self.geometry("1000x750")
        self.minsize(900, 640)
        self.configure(bg="#ffffff")
        
        self.current_frame = None
        self.frames = {}
        self.sidebar_buttons = {}

        self._build_styles()
        self._set_icon()
        self._build_layout()

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#ffffff")
        style.configure("Sidebar.TFrame", background="#f3f4f6")
        style.configure("Sidebar.TLabel", background="#f3f4f6", font=("Segoe UI", 12))
        style.configure("Sidebar.TButton", background="#f3f4f6", relief="flat", font=("Segoe UI", 10))
        style.map("Sidebar.TButton", background=[("active", "#e5e7eb")])
        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), background="#ffffff", foreground="#1f2937")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 12), background="#ffffff", foreground="#4b5563")

    def _set_icon(self):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, 'pill.ico')
        if not os.path.exists(icon_path) and getattr(sys, 'frozen', False):
            icon_path = os.path.join(os.path.dirname(sys.executable), 'pill.ico')
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

    # ------------------------------------------------------------------ #
    #  Helper: shorthand for self.translator.t
    # ------------------------------------------------------------------ #
    def _t(self, key, fallback=None):
        return self.translator.t(key, fallback)

    def _build_layout(self):
        # Sidebar
        self.sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        ttk.Label(self.sidebar, text="MedPulse", style="Sidebar.TLabel", font=("Segoe UI", 14, "bold")).pack(pady=(20, 10), padx=10, anchor="w")
        ttk.Label(self.sidebar, text=self._t("infusion_speed_calc", "Clinical Calculator"), style="Sidebar.TLabel", font=("Segoe UI", 9), foreground="#6b7280").pack(pady=(0, 20), padx=10, anchor="w")

        # Main Content
        self.main_content = ttk.Frame(self, style="TFrame")
        self.main_content.pack(side="right", fill="both", expand=True)
        
        # Header in Main Content
        self.header_frame = ttk.Frame(self.main_content, style="TFrame")
        self.header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        self.lang_btn = ttk.Button(self.header_frame, text="🌏 Language", command=self.toggle_language)
        self.lang_btn.pack(side="right", anchor="n")
        
        title_container = ttk.Frame(self.header_frame, style="TFrame")
        title_container.pack(side="left", fill="both", expand=True)
        
        self.title_label = ttk.Label(title_container, text="", style="Title.TLabel")
        self.title_label.pack(anchor="w")
        self.subtitle_label = ttk.Label(title_container, text="", style="Subtitle.TLabel")
        self.subtitle_label.pack(anchor="w", pady=(5,0))
        
        # Content Container
        self.content_container = ttk.Frame(self.main_content, style="TFrame")
        self.content_container.pack(fill="both", expand=True, padx=30, pady=10)

        # Define views — every label and description goes through _t()
        self.views = [
            ("abg",        self._t("abg_calc", "ABG Analysis"),      self._build_abg_tab,        self._t("desc_abg", "Rapid ABG Interpretation")),
            ("anion_gap",  self._t("ag_calc", "Anion Gap"),          self._build_anion_gap_tab,  self._t("desc_anion_gap", "Anion Gap Calculation")),
            ("winter",     self._t("winter_calc", "Winter's Formula"), self._build_winter_tab,   self._t("desc_winter", "Winter's Formula — Respiratory Compensation Check")),
            ("delta_gap",  self._t("delta_gap_calc", "Delta Gap"),   self._build_delta_gap_tab,  self._t("desc_delta_gap", "Delta Gap — Mixed Acid-Base Assessment")),
            ("infusion",   self._t("infusion_calc", "Infusion Rate"), self._build_infusion_tab,  self._t("desc_infusion", "Syringe Pump & Infusion Rate")),
            ("dilution",   self._t("dilution_calc", "Dilution"),     self._build_dilution_tab,   self._t("desc_dilution", "Powder Dilution Concentration")),
            ("insulin",    self._t("insulin_calc", "Insulin TDD"),   self._build_insulin_tab,    self._t("desc_insulin", "Insulin Total Daily Dose (TDD)")),
            ("antibiotic", self._t("antibiotic_calc", "Antibiotic Dose"), self._build_antibiotic_tab, self._t("desc_antibiotic", "Weight-based Antibiotic Dose")),
            ("burn",       self._t("burn_calc", "Burn (Parkland)"),  self._build_burn_tab,       self._t("desc_burn", "Parkland Burn Formula")),
            ("pediatrics", self._t("pediatrics_calc", "Pediatrics"), self._build_pediatrics_tab, self._t("desc_pediatrics", "Pediatric BSA & 4-2-1 Maintenance Fluid")),
            ("qsofa",      self._t("qsofa_calc", "qSOFA Score"),     self._build_qsofa_tab,      self._t("desc_qsofa", "Quick SOFA Score")),
            ("gcs",        self._t("gcs_calc", "GCS Score"),         self._build_gcs_tab,        self._t("desc_gcs", "Glasgow Coma Scale")),
            ("checklists", self._t("checklists_tab", "Checklists"),  self._build_checklist_tab,  self._t("desc_checklists", "Clinical Checklists")),
            ("settings",   self._t("settings_tab", "Settings"),      self._build_settings_tab,   self._t("desc_settings", "Manage calculators in sidebar")),
        ]
        
        self.render_sidebar()
        self.show_view("abg")

    def render_sidebar(self):
        # Clear existing buttons
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.destroy()
                
        self.sidebar_buttons.clear()
                
        for view_id, label, builder_func, desc in self.views:
            if not self.preferences.get(view_id, True) and view_id != "settings":
                continue
                
            btn = ttk.Button(self.sidebar, text="  " + label, style="Sidebar.TButton", command=lambda vid=view_id: self.show_view(vid))
            btn.pack(fill="x", padx=10, pady=2)
            self.sidebar_buttons[view_id] = btn

    def show_view(self, view_id):
        if self.current_frame:
            self.current_frame.pack_forget()
            
        view_info = next((v for v in self.views if v[0] == view_id), None)
        if not view_info:
            return
            
        _, label, builder_func, desc = view_info
        
        self.title_label.configure(text=label)
        self.subtitle_label.configure(text=desc)
        
        if view_id not in self.frames:
            frame = builder_func(self.content_container)
            self.frames[view_id] = frame
            
        self.current_frame = self.frames[view_id]
        self.current_frame.pack(fill="both", expand=True)

    def toggle_language(self):
        current = self.preferences.get("locale", "en")
        new_locale = "en" if current == "zh_CN" else "zh_CN"
        self.preferences["locale"] = new_locale
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=4)
        except Exception:
            pass
            
        # 1. Update translator
        self.translator = Translator(new_locale)
        set_global_locale(new_locale)
        
        # 2. Update window title
        self.title(self._t("app_title", "MedPulse"))
        
        # 3. Destroy current layout
        if hasattr(self, 'sidebar'): self.sidebar.destroy()
        if hasattr(self, 'main_content'): self.main_content.destroy()
        
        # 4. Clear cache
        self.frames.clear()
        self.current_frame = None
        
        # 5. Rebuild layout
        self._build_layout()

    def _build_settings_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        
        ttk.Label(frame, text=self._t("settings_instruction", "Select calculators to display in sidebar:"), font=("Segoe UI", 11), background="#ffffff").pack(anchor="w", pady=(0, 10))
        
        self.setting_vars = {}
        for view_id, label, _, _ in self.views:
            if view_id == "settings":
                continue
            var = tk.BooleanVar(value=self.preferences.get(view_id, True))
            self.setting_vars[view_id] = var
            cb = CustomCheckbox(frame, text=label, variable=var, bg="#ffffff")
            cb.pack(anchor="w", pady=2)
            
        def apply_settings():
            for view_id, var in self.setting_vars.items():
                self.preferences[view_id] = var.get()
            
            try:
                with open(self.settings_file, "w", encoding="utf-8") as f:
                    json.dump(self.preferences, f, ensure_ascii=False, indent=4)
            except Exception:
                pass
                
            self.render_sidebar()
            messagebox.showinfo(self._t("success", "Success"), self._t("settings_saved", "Sidebar updated and saved!"))
            
        ttk.Button(frame, text=self._t("btn_apply_settings", "Apply and Save"), command=apply_settings).pack(anchor="w", pady=(20, 0))
        return frame

    # --- Checklist Tab ---
    def _build_checklist_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        header = ttk.Frame(frame, style="TFrame")
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text=self._t("select_checklist", "Select Checklist"), background="#ffffff").pack(side="left", padx=(0, 8))
        self.checklists_data = {}
        options = []
        for filename in list_json_files("checklists"):
            data = load_json("checklists", filename)
            for item in data.get("items", []):
                title = item.get("title", "Unknown")
                title_t = self._t("chk_%s_title" % item.get('id', 'unknown'), title)
                self.checklists_data[title_t] = item
                options.append(title_t)
        self.checklist_var = tk.StringVar()
        combo = ttk.Combobox(header, textvariable=self.checklist_var, values=options, state="readonly", width=40)
        combo.pack(side="left")
        
        self.checklist_container = ttk.Frame(frame, style="TFrame")
        self.checklist_container.pack(fill="both", expand=True)
        
        def on_select(event):
            for widget in self.checklist_container.winfo_children():
                widget.destroy()
            selected_title = self.checklist_var.get()
            if not selected_title or selected_title not in self.checklists_data:
                return
            checklist_data = self.checklists_data[selected_title]
            ttk.Label(self.checklist_container, text=self._t("checklist_note", "For reference only."), font=("Segoe UI", 9, "italic"), foreground="#555555", background="#ffffff").pack(anchor="w", pady=(0, 12))
            
            checklist_id = checklist_data.get("id", "unknown")
            for idx, item in enumerate(checklist_data.get("checks", [])):
                text = self._t("chk_%s_item_%d" % (checklist_id, idx), item)
                cb = CustomCheckbox(self.checklist_container, text=text, variable=tk.BooleanVar(), bg="#ffffff")
                cb.pack(anchor="w", pady=4, padx=10)

        combo.bind("<<ComboboxSelected>>", on_select)
        if options:
            combo.current(0)
            on_select(None)
        return frame

    # --- Calculators (Forms) ---
    def _add_entry(self, parent, row, label, variable, focus_out=None):
        ttk.Label(parent, text=label, background="#ffffff", font=("Segoe UI", 10)).grid(row=row, column=0, sticky="w", padx=(0, 15), pady=8)
        entry = ttk.Entry(parent, textvariable=variable, width=28, font=("Segoe UI", 10))
        entry.grid(row=row, column=1, sticky="w", pady=8)
        if focus_out:
            entry.bind("<FocusOut>", focus_out)
        return entry

    def _make_result_box(self, parent):
        widget = tk.Text(parent, height=12, wrap="word", font=("Consolas", 11), bg="#f8fafc", relief="flat", padx=10, pady=10)
        widget.pack(fill="both", expand=True)
        widget.configure(state="disabled")
        return widget

    def _set_result(self, widget, text, latex_formula=None):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        if latex_formula:
            try:
                from medpulse.ui.windows.renderer import render_formula
                photo = render_formula(latex_formula)
                self._image_cache.append(photo)
                if len(self._image_cache) > 20:
                    self._image_cache = self._image_cache[-20:]
                widget.image_create("1.0", image=photo)
                widget.insert("end", "\n\n")
            except Exception:
                pass
        widget.insert("end", text)
        widget.configure(state="disabled")

    def _handle_error(self, exc):
        if isinstance(exc, ValidationError):
            message = str(exc) or self._t("error_general", "Validation Error")
        else:
            message = str(exc)
        messagebox.showerror(self._t("calc_error", "Calculation Error"), message)

    def _build_anion_gap_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        form = ttk.Frame(frame, style="TFrame")
        form.pack(anchor="nw", fill="x")
        self.ag_vars = {"na": tk.StringVar(), "cl": tk.StringVar(), "hco3": tk.StringVar(), "albumin": tk.StringVar()}
        self._add_entry(form, 0, self._t("input_na", "Na+ (mmol/L)"), self.ag_vars["na"])
        self._add_entry(form, 1, self._t("input_cl", "Cl- (mmol/L)"), self.ag_vars["cl"])
        self._add_entry(form, 2, self._t("input_hco3", "HCO3- (mmol/L)"), self.ag_vars["hco3"])
        self._add_entry(form, 3, self._t("input_albumin", "Albumin (g/L) (Optional)"), self.ag_vars["albumin"])
        ttk.Button(frame, text=self._t("btn_calculate", "Calculate"), command=self._calculate_anion_gap).pack(anchor="w", pady=(15, 10))
        self.ag_result = self._make_result_box(frame)
        return frame

    def _calculate_anion_gap(self):
        try:
            result = anion_gap(self.ag_vars["na"].get(), self.ag_vars["cl"].get(), self.ag_vars["hco3"].get(), self.ag_vars["albumin"].get())
            self._set_result(self.ag_result, self.formatter.format_calculation(result), latex_formula=getattr(result, "latex_formula", None))
        except Exception as exc:
            self._handle_error(exc)

    def _build_winter_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        form = ttk.Frame(frame, style="TFrame")
        form.pack(anchor="nw", fill="x")
        self.winter_vars = {"hco3": tk.StringVar(), "pco2": tk.StringVar()}
        self._add_entry(form, 0, self._t("input_hco3", "HCO3- (mmol/L)"), self.winter_vars["hco3"])
        self._add_entry(form, 1, self._t("input_pco2", "pCO2 (mmHg)"), self.winter_vars["pco2"])
        ttk.Button(frame, text=self._t("btn_calculate", "Calculate"), command=self._calculate_winter).pack(anchor="w", pady=(15, 10))
        self.winter_result = self._make_result_box(frame)
        return frame

    def _calculate_winter(self):
        try:
            result = winter_expected_pco2(self.winter_vars["hco3"].get(), self.winter_vars["pco2"].get())
            self._set_result(self.winter_result, self.formatter.format_calculation(result), latex_formula=getattr(result, "latex_formula", None))
        except Exception as exc:
            self._handle_error(exc)

    def _build_abg_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        form = ttk.Frame(frame, style="TFrame")
        form.pack(anchor="nw", fill="x")
        self.abg_vars = {"ph": tk.StringVar(), "pco2": tk.StringVar(), "hco3": tk.StringVar()}
        self._add_entry(form, 0, self._t("input_ph", "pH"), self.abg_vars["ph"])
        self._add_entry(form, 1, self._t("input_pco2", "pCO2 (mmHg)"), self.abg_vars["pco2"])
        self._add_entry(form, 2, self._t("input_hco3", "HCO3- (mmol/L)"), self.abg_vars["hco3"])
        ttk.Button(frame, text=self._t("btn_calculate", "Calculate"), command=self._analyze_abg).pack(anchor="w", pady=(15, 10))
        self.abg_result = self._make_result_box(frame)
        return frame

    def _analyze_abg(self):
        try:
            analysis = analyze_abg(self.abg_vars["ph"].get(), self.abg_vars["pco2"].get(), self.abg_vars["hco3"].get())
            self._set_result(self.abg_result, self.formatter.format_abg(analysis))
        except Exception as exc:
            self._handle_error(exc)
            
    def _build_delta_gap_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        form = ttk.Frame(frame, style="TFrame")
        form.pack(anchor="nw", fill="x")
        self.dg_vars = {"ag": tk.StringVar(), "hco3": tk.StringVar()}
        self._add_entry(form, 0, self._t("input_ag", "Anion Gap (mmol/L)"), self.dg_vars["ag"])
        self._add_entry(form, 1, self._t("input_hco3", "HCO3- (mmol/L)"), self.dg_vars["hco3"])
        ttk.Button(frame, text=self._t("btn_calculate", "Calculate"), command=lambda: self._run_calc(delta_gap, [self.dg_vars["ag"].get(), self.dg_vars["hco3"].get()], self.dg_result)).pack(anchor="w", pady=(15, 10))
        self.dg_result = self._make_result_box(frame)
        return frame
        
    def _run_calc(self, func, args, result_widget):
        try:
            result = func(*args)
            self._set_result(result_widget, self.formatter.format_calculation(result), latex_formula=getattr(result, "latex_formula", None))
        except Exception as exc:
            self._handle_error(exc)

    def _build_infusion_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        form = ttk.Frame(frame, style="TFrame")
        form.pack(anchor="nw", fill="x")
        self.infusion_vars = {"weight": tk.StringVar(), "dose": tk.StringVar(), "rate": tk.StringVar(), "concentration_mode": tk.StringVar(value="mcg/mL"), "concentration_value": tk.StringVar(), "volume_ml": tk.StringVar()}
        self._add_entry(form, 0, self._t("input_weight", "Weight (kg)"), self.infusion_vars["weight"])
        self._add_entry(form, 1, self._t("input_target_dose", "Target Dose (mcg/kg/min)"), self.infusion_vars["dose"])
        self._add_entry(form, 2, self._t("input_current_rate", "Current Rate (mL/h)"), self.infusion_vars["rate"])
        ttk.Label(form, text=self._t("mode", "Mode:"), background="#ffffff").grid(row=3, column=0, sticky="w", padx=(0, 15), pady=8)
        mode = ttk.Combobox(form, textvariable=self.infusion_vars["concentration_mode"], values=["mcg/mL", "mg/mL", "total mcg / volume mL", "total mg / volume mL"], state="readonly", width=26)
        mode.grid(row=3, column=1, sticky="w", pady=8)
        self._add_entry(form, 4, self._t("input_concentration_value", "Concentration / Total Dose"), self.infusion_vars["concentration_value"], focus_out=self._parse_concentration_expression)
        self._add_entry(form, 5, self._t("input_volume_total", "Volume (mL)"), self.infusion_vars["volume_ml"])
        buttons = ttk.Frame(frame, style="TFrame")
        buttons.pack(anchor="w", pady=(15, 10))
        ttk.Button(buttons, text=self._t("mode_dose_to_rate", "Dose → Rate"), command=self._calculate_infusion_rate).pack(side="left", padx=(0, 10))
        ttk.Button(buttons, text=self._t("mode_rate_to_dose", "Rate → Dose"), command=self._calculate_infusion_dose).pack(side="left")
        self.infusion_result = self._make_result_box(frame)
        self._set_result(self.infusion_result, self._t("checklist_note", "For reference only."))
        return frame
        
    def _parse_concentration_expression(self, _event=None):
        import re
        raw = self.infusion_vars["concentration_value"].get().strip()
        pattern = re.compile(r'^([\d.]+)\s*(mg|mcg|μg|ug)\s*/\s*([\d.]+)\s*ml$', re.IGNORECASE)
        match = pattern.match(raw)
        if not match: return
        amount_str, unit_str, volume_str = match.group(1), match.group(2).lower(), match.group(3)
        self.infusion_vars["concentration_mode"].set("total mg / volume mL" if unit_str == "mg" else "total mcg / volume mL")
        self.infusion_vars["concentration_value"].set(amount_str)
        self.infusion_vars["volume_ml"].set(volume_str)

    def _resolve_infusion_concentration(self):
        mode, value, volume = self.infusion_vars["concentration_mode"].get(), self.infusion_vars["concentration_value"].get(), self.infusion_vars["volume_ml"].get()
        if mode == "total mcg / volume mL": return concentration_from_amount(value, "mcg", volume), "mcg/mL", "%s %s mcg / %s mL" % (self._t('fmt_total_amount', 'Total'), value, volume)
        if mode == "total mg / volume mL": return concentration_from_amount(value, "mg", volume), "mcg/mL", "%s %s mg / %s mL" % (self._t('fmt_total_amount', 'Total'), value, volume)
        return value, mode, "%s %s" % (value, mode)

    def _calculate_infusion_rate(self):
        try:
            concentration, unit, label = self._resolve_infusion_concentration()
            result = infusion_rate_result(
                self.infusion_vars["dose"].get(),
                self.infusion_vars["weight"].get(),
                concentration,
                unit,
            )
            result.metadata["mode"] = label
            self._set_result(self.infusion_result, self.formatter.format_calculation(result))
        except Exception as exc:
            self._handle_error(exc)

    def _calculate_infusion_dose(self):
        try:
            concentration, unit, label = self._resolve_infusion_concentration()
            result = infusion_dose_result(
                self.infusion_vars["rate"].get(),
                self.infusion_vars["weight"].get(),
                concentration,
                unit,
            )
            result.metadata["mode"] = label
            self._set_result(self.infusion_result, self.formatter.format_calculation(result))
        except Exception as exc:
            self._handle_error(exc)

    def _build_pediatrics_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        ttk.Label(frame, text=self._t("mosteller_bsa", "Mosteller BSA"), font=("Segoe UI", 11, "bold"), background="#ffffff").pack(anchor="w")
        bsa_form = ttk.Frame(frame, style="TFrame")
        bsa_form.pack(anchor="nw", fill="x")
        self.bsa_vars = {"weight": tk.StringVar(), "height": tk.StringVar()}
        self._add_entry(bsa_form, 0, self._t("input_weight", "Weight (kg)"), self.bsa_vars["weight"])
        self._add_entry(bsa_form, 1, self._t("input_height", "Height (cm)"), self.bsa_vars["height"])
        ttk.Button(frame, text=self._t("btn_calc_bsa", "Calculate BSA"), command=lambda: self._run_calc(mosteller_bsa, [self.bsa_vars["weight"].get(), self.bsa_vars["height"].get()], self.bsa_result)).pack(anchor="w", pady=(8, 4))
        self.bsa_result = self._make_result_box(frame)
        ttk.Label(frame, text=self._t("maint_fluid_421", "4-2-1 Maintenance Fluid"), font=("Segoe UI", 11, "bold"), background="#ffffff").pack(anchor="w", pady=(15, 0))
        fluid_form = ttk.Frame(frame, style="TFrame")
        fluid_form.pack(anchor="nw", fill="x")
        self.fluid_vars = {"weight": tk.StringVar()}
        self._add_entry(fluid_form, 0, self._t("input_weight", "Weight (kg)"), self.fluid_vars["weight"])
        ttk.Button(frame, text=self._t("btn_calc_fluid", "Calculate Fluid"), command=lambda: self._run_calc(maintenance_fluid_421, [self.fluid_vars["weight"].get()], self.fluid_result)).pack(anchor="w", pady=(8, 4))
        self.fluid_result = self._make_result_box(frame)
        return frame

    def _build_qsofa_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        form = ttk.Frame(frame, style="TFrame")
        form.pack(anchor="nw", fill="x")
        self.qsofa_vars = {"respiratory_rate": tk.StringVar(), "sbp": tk.StringVar(), "altered_mentation": tk.BooleanVar(value=False)}
        self._add_entry(form, 0, self._t("input_rr", "Respiratory Rate (bpm)"), self.qsofa_vars["respiratory_rate"])
        self._add_entry(form, 1, self._t("input_sbp", "Systolic BP (mmHg)"), self.qsofa_vars["sbp"])
        cb = CustomCheckbox(form, text=self._t("input_am", "Altered Mentation (GCS < 15)"), variable=self.qsofa_vars["altered_mentation"], bg="#ffffff")
        cb.grid(row=2, column=1, sticky="w", pady=8)
        ttk.Button(frame, text=self._t("btn_calculate", "Calculate"), command=self._score_qsofa).pack(anchor="w", pady=(15, 10))
        self.qsofa_result = self._make_result_box(frame)
        return frame

    def _score_qsofa(self):
        try:
            rr = float(self.qsofa_vars["respiratory_rate"].get())
            sbp = float(self.qsofa_vars["sbp"].get())
            result = self.score_service.calculate("qsofa", {"respiratory_rate_high": rr >= 22.0, "altered_mentation": self.qsofa_vars["altered_mentation"].get(), "sbp_low": sbp <= 100.0})
            self._set_result(self.qsofa_result, self.formatter.format_score(result))
        except Exception as exc:
            self._handle_error(exc)

    def _build_gcs_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        form = ttk.Frame(frame, style="TFrame")
        form.pack(anchor="nw", fill="x")
        self.gcs_vars = {}
        for row_index, item in enumerate(self._gcs_definition.get("items", [])):
            label_text = self._t("gcs_%s" % item['id'], item["label"])
            ttk.Label(form, text=label_text, background="#ffffff").grid(row=row_index, column=0, sticky="w", padx=(0, 15), pady=8)
            select_text = self._t("select_option", "-- Select Option --")
            display_to_id = {select_text: ""}
            options = [select_text]
            for option in item.get("options", []):
                opt_text = self._t("gcs_%s_%s" % (item['id'], option['id']), option["label"])
                display_to_id[opt_text] = option["id"]
                options.append(opt_text)
            self._gcs_option_maps[item["id"]] = display_to_id
            var = tk.StringVar(value=options[0])
            combo = ttk.Combobox(form, textvariable=var, values=options, state="readonly", width=28)
            combo.grid(row=row_index, column=1, sticky="w", pady=8)
            self.gcs_vars[item["id"]] = var
        ttk.Button(frame, text=self._t("btn_calculate", "Calculate"), command=self._score_gcs).pack(anchor="w", pady=(15, 10))
        self.gcs_result = self._make_result_box(frame)
        return frame

    def _score_gcs(self):
        try:
            answers = {}
            for item in self._gcs_definition.get("items", []):
                display_value = self.gcs_vars[item["id"]].get()
                answer = self._gcs_option_maps[item["id"]].get(display_value, "")
                if not answer: raise ValidationError(self._t("err_gcs_incomplete", "Please select all GCS components!"))
                answers[item["id"]] = answer
            result = self.score_service.calculate("gcs", answers)
            self._set_result(self.gcs_result, self.formatter.format_score(result))
        except Exception as exc:
            self._handle_error(exc)

    # --- New Calculators ---
    def _build_dilution_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        form = ttk.Frame(frame, style="TFrame")
        form.pack(anchor="nw", fill="x")
        self.dil_vars = {"amount": tk.StringVar(), "volume": tk.StringVar()}
        self._add_entry(form, 0, self._t("input_drug_amount", "Drug Amount (mg)"), self.dil_vars["amount"])
        self._add_entry(form, 1, self._t("input_diluent_vol", "Diluent Volume (mL)"), self.dil_vars["volume"])
        ttk.Button(frame, text=self._t("btn_calc_concentration", "Calculate Concentration"), command=lambda: self._run_calc(dilute_powder, [self.dil_vars["amount"].get(), self.dil_vars["volume"].get()], self.dil_result)).pack(anchor="w", pady=(15, 10))
        self.dil_result = self._make_result_box(frame)
        return frame

    def _build_insulin_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        
        ttk.Label(frame, text=self._t("insulin_calc", "Insulin TDD"), font=("Segoe UI", 11, "bold"), background="#ffffff").pack(anchor="w")
        form1 = ttk.Frame(frame, style="TFrame")
        form1.pack(anchor="nw", fill="x")
        self.ins_vars = {"weight": tk.StringVar()}
        self._add_entry(form1, 0, self._t("input_weight", "Weight (kg)"), self.ins_vars["weight"])
        ttk.Button(frame, text=self._t("btn_calc_tdd", "Estimate TDD"), command=lambda: self._run_calc(insulin_tdd, [self.ins_vars["weight"].get()], self.ins_result)).pack(anchor="w", pady=(8, 4))
        self.ins_result = self._make_result_box(frame)

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=15)
        
        ttk.Label(frame, text=self._t("glucose_insulin_calc", "Glucose-Insulin Neutralization"), font=("Segoe UI", 11, "bold"), background="#ffffff").pack(anchor="w")
        form2 = ttk.Frame(frame, style="TFrame")
        form2.pack(anchor="nw", fill="x")
        self.gi_vars = {"conc": tk.StringVar(), "vol": tk.StringVar(), "ratio": tk.StringVar(value="4")}
        self._add_entry(form2, 0, self._t("input_glucose_conc", "Glucose Concentration (%)"), self.gi_vars["conc"])
        self._add_entry(form2, 1, self._t("input_glucose_vol", "Volume (mL)"), self.gi_vars["vol"])
        self._add_entry(form2, 2, self._t("input_insulin_ratio", "Ratio (g/U)"), self.gi_vars["ratio"])
        
        ttk.Button(frame, text=self._t("btn_calc_glucose_insulin", "Calculate Insulin"), command=lambda: self._run_calc(glucose_insulin, [self.gi_vars["conc"].get(), self.gi_vars["vol"].get(), self.gi_vars["ratio"].get()], self.gi_result)).pack(anchor="w", pady=(8, 4))
        self.gi_result = self._make_result_box(frame)

        return frame

    def _build_antibiotic_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        form = ttk.Frame(frame, style="TFrame")
        form.pack(anchor="nw", fill="x")
        self.ab_vars = {"weight": tk.StringVar(), "dose": tk.StringVar()}
        self._add_entry(form, 0, self._t("input_weight", "Weight (kg)"), self.ab_vars["weight"])
        self._add_entry(form, 1, self._t("input_dose_req", "Dose Requirement (mg/kg)"), self.ab_vars["dose"])
        ttk.Button(frame, text=self._t("btn_calc_total_dose", "Calculate Total Dose"), command=lambda: self._run_calc(antibiotic_dose, [self.ab_vars["weight"].get(), self.ab_vars["dose"].get()], self.ab_result)).pack(anchor="w", pady=(15, 10))
        self.ab_result = self._make_result_box(frame)
        return frame

    def _build_burn_tab(self, parent):
        frame = ttk.Frame(parent, style="TFrame")
        form = ttk.Frame(frame, style="TFrame")
        form.pack(anchor="nw", fill="x")
        self.burn_vars = {"weight": tk.StringVar(), "tbsa": tk.StringVar()}
        self._add_entry(form, 0, self._t("input_weight", "Weight (kg)"), self.burn_vars["weight"])
        self._add_entry(form, 1, self._t("input_tbsa", "TBSA (%)"), self.burn_vars["tbsa"])
        
        def run_burn():
            try:
                res = parkland_formula(self.burn_vars["weight"].get(), self.burn_vars["tbsa"].get())
                self._set_result(self.burn_result, self.formatter.format_calculation(res), latex_formula=res.latex_formula)
            except Exception as e:
                self._handle_error(e)
                
        ttk.Button(frame, text=self._t("btn_calc_burn", "Calculate Burn Fluids"), command=run_burn).pack(anchor="w", pady=(15, 10))
        self.burn_result = self._make_result_box(frame)
        return frame

def launch(locale="en"):
    app = MedPulseTkApp(locale=locale)
    app.mainloop()
