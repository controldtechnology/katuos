// Katu OS — Plasma default layout script
// Executado via plasma-apply-desktoptheme ou hook de configuração

// Painel inferior
var panel = new Panel;
panel.location = "bottom";
panel.height = 56;
panel.alignment = "center";
panel.lengthMode = "fit";
panel.floating = true;
panel.hiding = "none";

// Widgets do painel
var launcherId = panel.addWidget("org.kde.plasma.kickoff");
try {
    var launcher = panel.widgetById(launcherId);
    launcher.currentConfigGroup = ["General"];
    launcher.writeConfig("icon", "katu-logo");
} catch (e) {
    // A falha de personalização não deve impedir a criação do launcher.
}
panel.addWidget("org.kde.plasma.icontasks");         // Tarefas
panel.addWidget("org.kde.plasma.marginsseparator"); // Separador
panel.addWidget("org.kde.plasma.systemtray");        // Bandeja do sistema
panel.addWidget("org.kde.plasma.digitalclock");      // Relógio
