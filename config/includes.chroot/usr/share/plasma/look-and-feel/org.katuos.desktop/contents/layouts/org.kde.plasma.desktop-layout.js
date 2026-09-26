// Katu OS — layout padrão do Plasma.
// Executado ao aplicar este pacote look-and-feel.

var panel = new Panel;
panel.location = "bottom";
panel.height = 52;
panel.hiding = "none";

// Lançador Katu com ícone oficial
var katuMenu = panel.addWidget("org.kde.plasma.kickoff");
katuMenu.currentConfigGroup = ["General"];
katuMenu.writeConfig("icon", "katu-logo");
katuMenu.writeConfig("showButtonBox", false);

// Tarefas abertas
panel.addWidget("org.kde.plasma.icontasks");
panel.addWidget("org.kde.plasma.marginsseparator");
panel.addWidget("org.kde.plasma.systemtray");

// Relógio com data em português
var clock = panel.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", true);
clock.writeConfig("dateDisplayFormat", "LongDate");
