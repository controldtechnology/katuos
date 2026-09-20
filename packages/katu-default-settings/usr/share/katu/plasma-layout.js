// Katu OS — Plasma default layout script
// Executado via plasma-apply-desktoptheme ou hook de configuração

// Painel inferior
var panel = new Panel;
panel.location = "bottom";
panel.height = 48;
panel.alignment = "center";
panel.hiding = "none";

// Widgets do painel
panel.addWidget("org.kde.plasma.kickoff");          // Menu Katu (Application Launcher)
panel.addWidget("org.kde.plasma.icontasks");         // Tarefas
panel.addWidget("org.kde.plasma.marginsseparator"); // Separador
panel.addWidget("org.kde.plasma.systemtray");        // Bandeja do sistema
panel.addWidget("org.kde.plasma.digitalclock");      // Relógio
