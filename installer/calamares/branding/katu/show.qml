/* Katu OS — Calamares Installation Slides */

import QtQuick 2.15
import QtQuick.Controls 2.15
import Calamares 1.0 as Calamares

Calamares.Slideshow {
    id: slideshow

    // Cores Katu
    property string katuGreen:   "#2ecc71"
    property string katuDark:    "#1a1a1a"
    property string katuWhite:   "#f8f9fa"
    property string katuForest:  "#1a5c2a"

    Rectangle {
        anchors.fill: parent
        color: katuDark

        SwipeView {
            id: swipeView
            anchors.fill: parent
            currentIndex: 0

            // === Slide 1: Bem-vindo ===
            Item {
                Column {
                    anchors.centerIn: parent
                    spacing: 24
                    width: parent.width * 0.7

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "Bem-vindo ao Katu OS"
                        font.pixelSize: 28
                        font.weight: Font.Bold
                        color: katuWhite
                    }
                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "Livre. Brasileiro. Para todos."
                        font.pixelSize: 16
                        color: katuGreen
                        font.italic: true
                    }
                    Text {
                        width: parent.width
                        text: "O Katu OS está sendo instalado no seu computador. "
                            + "Em alguns minutos você terá um sistema Linux moderno, "
                            + "em português, pronto para usar."
                        font.pixelSize: 14
                        color: "#cccccc"
                        wrapMode: Text.WordWrap
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }

            // === Slide 2: KDE Plasma ===
            Item {
                Column {
                    anchors.centerIn: parent
                    spacing: 24
                    width: parent.width * 0.7

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "KDE Plasma"
                        font.pixelSize: 28
                        font.weight: Font.Bold
                        color: katuWhite
                    }
                    Text {
                        width: parent.width
                        text: "O Katu OS utiliza o KDE Plasma, um dos ambientes de desktop "
                            + "mais modernos do Linux. Rápido, personalizável e bonito."
                        font.pixelSize: 14
                        color: "#cccccc"
                        wrapMode: Text.WordWrap
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }

            // === Slide 3: Software ===
            Item {
                Column {
                    anchors.centerIn: parent
                    spacing: 24
                    width: parent.width * 0.7

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "Software para tudo"
                        font.pixelSize: 28
                        font.weight: Font.Bold
                        color: katuWhite
                    }
                    Text {
                        width: parent.width
                        text: "Firefox, LibreOffice, reprodutor de vídeos e muito mais "
                            + "já estão instalados. Descubra milhares de aplicativos "
                            + "adicionais na loja Katu OS."
                        font.pixelSize: 14
                        color: "#cccccc"
                        wrapMode: Text.WordWrap
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }

            // === Slide 4: Segurança ===
            Item {
                Column {
                    anchors.centerIn: parent
                    spacing: 24
                    width: parent.width * 0.7

                    Text {
                        anchors.horizontalCenter: parent.horizontalCenter
                        text: "Seguro e privado"
                        font.pixelSize: 28
                        font.weight: Font.Bold
                        color: katuWhite
                    }
                    Text {
                        width: parent.width
                        text: "O Katu OS é construído sobre a base sólida do Debian. "
                            + "Sem telemetria oculta. Sem propagandas. "
                            + "Seus dados são seus."
                        font.pixelSize: 14
                        color: "#cccccc"
                        wrapMode: Text.WordWrap
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
            }

        }

        // Indicadores de slide
        PageIndicator {
            anchors {
                bottom: swipeView.bottom
                horizontalCenter: swipeView.horizontalCenter
                bottomMargin: 20
            }
            count: swipeView.count
            currentIndex: swipeView.currentIndex

            delegate: Rectangle {
                implicitWidth: currentIndex === index ? 24 : 8
                implicitHeight: 8
                radius: height / 2
                color: currentIndex === index ? katuGreen : "#555555"
                Behavior on implicitWidth { NumberAnimation { duration: 200 } }
            }
        }
    }

    // Auto-avanço dos slides
    Timer {
        interval: 6000
        running: true
        repeat: true
        onTriggered: {
            var next = swipeView.currentIndex + 1
            swipeView.currentIndex = next < swipeView.count ? next : 0
        }
    }
}
