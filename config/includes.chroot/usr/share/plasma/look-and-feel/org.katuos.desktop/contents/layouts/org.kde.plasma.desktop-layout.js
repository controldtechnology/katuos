// Katu OS — layout padrão do Plasma.
// O Plasma executa este arquivo ao aplicar o pacote look-and-feel.

var panel = new Panel;
panel.location = "bottom";
panel.height = 56;
panel.hiding = "none";
panel.alignment = "center";
panel.lengthMode = "fit";
panel.floating = true;

// Menu de aplicativos Katu e tarefas abertas.
var launcherId = panel.addWidget("org.kde.plasma.kickoff");
try {
    var launcher = panel.widgetById(launcherId);
    launcher.currentConfigGroup = ["General"];
    launcher.writeConfig("icon", "katu-logo");
} catch (e) {
    // A falha de personalização não deve impedir a criação do launcher.
}
panel.addWidget("org.kde.plasma.icontasks");
panel.addWidget("org.kde.plasma.marginsseparator");
panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.digitalclock");
