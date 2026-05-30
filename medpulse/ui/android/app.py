"""Minimal Kivy app scaffold."""

def create_app():
    try:
        from kivy.app import App
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Kivy is not installed in this environment.") from exc

    class MedPulseAndroidApp(App):
        def build(self):  # pragma: no cover - optional dependency
            from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.label import Label
            from kivy.uix.checkbox import CheckBox
            from kivy.uix.spinner import Spinner
            from medpulse.core.resources import load_json, list_json_files
            from medpulse.i18n import Translator, set_global_locale

            # For now, Android just defaults to English, but uses the exact same resources
            locale = "en"
            translator = Translator(locale)
            set_global_locale(locale)

            tp = TabbedPanel(do_default_tab=False)
            
            # Checklist Tab
            checklist_tab = TabbedPanelItem(text=translator.t("checklists_tab", "Checklists"))
            layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            
            checklists_data = {}
            options = []
            for filename in list_json_files("checklists"):
                data = load_json("checklists", filename)
                for item in data.get("items", []):
                    title = item.get("title", "Unknown")
                    title_t = translator.t("chk_%s_title" % item.get('id', 'unknown'), title)
                    checklists_data[title_t] = item
                    options.append(title_t)
            
            spinner = Spinner(
                text=options[0] if options else translator.t("select_checklist", "Select Checklist"), 
                values=options, 
                size_hint_y=None, 
                height=44
            )
            layout.add_widget(spinner)
            
            checks_layout = BoxLayout(orientation='vertical', spacing=5)
            layout.add_widget(checks_layout)
            
            def update_checks(spinner_instance, text):
                checks_layout.clear_widgets()
                if text in checklists_data:
                    item = checklists_data[text]
                    checklist_id = item.get("id", "unknown")
                    for idx, check in enumerate(item.get("checks", [])):
                        check_t = translator.t("chk_%s_item_%d" % (checklist_id, idx), check)
                        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=44)
                        cb = CheckBox(size_hint_x=0.15)
                        lbl = Label(text=check_t, size_hint_x=0.85, halign='left', valign='middle')
                        lbl.bind(size=lbl.setter('text_size'))  # Wrap text properly
                        row.add_widget(cb)
                        row.add_widget(lbl)
                        checks_layout.add_widget(row)
                        
            spinner.bind(text=update_checks)
            if options:
                update_checks(spinner, options[0])
            
            checklist_tab.add_widget(layout)
            tp.add_widget(checklist_tab)
            
            return tp

    return MedPulseAndroidApp()

