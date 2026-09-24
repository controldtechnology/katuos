// Katu OS — Plasma Splash Screen
// Exibido durante o carregamento da sessão KDE

import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    color: "#0d1117"

    property int stage: 0

    // Logo central
    Image {
        id: logo
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -40
        source: "/usr/share/pixmaps/katu-logo.png"
        width: 180
        height: 72
        fillMode: Image.PreserveAspectFit
        smooth: true

        opacity: 0
        Behavior on opacity { NumberAnimation { duration: 400 } }

        Component.onCompleted: logo.opacity = 1
    }

    // Tagline
    Text {
        anchors {
            horizontalCenter: parent.horizontalCenter
            top: logo.bottom
            topMargin: 16
        }
        text: "Livre. Brasileiro. Para todos."
        color: "#8b949e"
        font.pixelSize: 13
        font.family: "Noto Sans"
        font.letterSpacing: 0.5

        opacity: 0
        Behavior on opacity { NumberAnimation { duration: 600; easing.type: Easing.InOutQuad } }
        Component.onCompleted: opacity = 1
    }

    // Barra de progresso
    Rectangle {
        id: progressBar
        anchors {
            bottom: parent.bottom
            bottomMargin: 80
            horizontalCenter: parent.horizontalCenter
        }
        width: 200
        height: 2
        radius: 1
        color: "#30363d"

        Rectangle {
            id: progressFill
            height: parent.height
            width: parent.width * (stage / 5)
            radius: 1
            color: "#00c853"
            Behavior on width { NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }
        }
    }

    // Versão
    Text {
        anchors {
            bottom: parent.bottom
            horizontalCenter: parent.horizontalCenter
            bottomMargin: 24
        }
        text: "Katu OS 1.0"
        color: "#30363d"
        font.pixelSize: 11
        font.family: "Noto Sans"
    }
}
