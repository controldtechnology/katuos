// Katu OS — KDE Plasma Panel Layout
// Painel único na base, estilo macOS/Windows com lançador Katu

var plasma = getApiVersion(1);

var layout = {
    desktops: [{
        applets: [],
        wallpaperPlugin: "org.kde.image",
        wallpaper: {
            "Image": "/usr/share/wallpapers/katu/contents/images/katu-amazonia-4k.png",
            "FillMode": 2
        }
    }],
    panels: [{
        location: "bottom",
        height: 48,
        hiding: "none",
        applets: [
            { plugin: "org.kde.plasma.kickoff",        config: { icon: "katu-logo", showButtonsFor: "power" } },
            { plugin: "org.kde.plasma.icontasks",      config: { launchers: [
                "applications:firefox-esr.desktop",
                "applications:org.kde.dolphin.desktop",
                "applications:org.kde.konsole.desktop",
                "applications:systemsettings.desktop"
            ]}},
            { plugin: "org.kde.plasma.marginsseparator" },
            { plugin: "org.kde.plasma.systemtray" },
            { plugin: "org.kde.plasma.digitalclock",   config: { dateFormat: "ddd, d MMM", use24hFormat: 2 } }
        ]
    }]
};
