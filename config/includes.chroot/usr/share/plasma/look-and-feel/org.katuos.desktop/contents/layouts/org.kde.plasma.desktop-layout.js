// Katu OS — layout padrão do Plasma.
// O Plasma executa este arquivo ao aplicar o pacote look-and-feel.

var panel = new Panel;
panel.location = "bottom";
panel.height = 48;
panel.hiding = "none";

// Menu de aplicativos Katu e tarefas abertas.
panel.addWidget("org.kde.plasma.kickoff");
panel.addWidget("org.kde.plasma.icontasks");
panel.addWidget("org.kde.plasma.marginsseparator");
panel.addWidget("org.kde.plasma.systemtray");
panel.addWidget("org.kde.plasma.digitalclock");
