// Katu OS SDDM Theme — Amazônia Dark
// Livre. Brasileiro. Para todos.

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#0d1117"

    property int sessionIndex: sessionModel.lastIndex

    // Fundo — wallpaper Katu Amazônia
    Image {
        id: background
        anchors.fill: parent
        source: config.background || "background.jpg"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        cache: false
    }

    // Overlay escuro — mantém legibilidade
    Rectangle {
        anchors.fill: parent
        color: "#0d1117"
        opacity: 0.72
    }

    // Linha accent verde no topo
    Rectangle {
        anchors { top: parent.top; left: parent.left; right: parent.right }
        height: 2
        color: "#00c853"
        opacity: 0.8
    }

    // Logo + tagline (canto inferior esquerdo)
    Column {
        anchors {
            left: parent.left
            bottom: parent.bottom
            margins: 48
        }
        spacing: 6

        Image {
            id: logoKatu
            source: "logo.png"
            width: 110
            height: 44
            fillMode: Image.PreserveAspectFit
            smooth: true
            opacity: 0.90
        }

        Text {
            text: "Livre. Brasileiro. Para todos."
            font.pixelSize: 11
            color: "#8b949e"
            font.family: "Noto Sans"
            font.letterSpacing: 0.5
        }
    }

    // Relógio (canto superior direito)
    Column {
        anchors {
            right: parent.right
            top: parent.top
            topMargin: 48
            rightMargin: 48
        }
        spacing: 2

        Clock {
            id: clock
            anchors.horizontalCenter: parent.horizontalCenter
            timeFont.pixelSize: 42
            timeFont.family: "Noto Sans"
            timeFont.weight: Font.Light
            color: "#e6edf3"
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatDate(new Date(), "dddd, d 'de' MMMM")
            font.pixelSize: 13
            color: "#8b949e"
            font.family: "Noto Sans"
        }
    }

    // Painel central de login
    Rectangle {
        id: loginPanel
        anchors.centerIn: parent
        width: 360
        height: 420
        color: "#0d1117"
        radius: 12
        border.color: "#30363d"
        border.width: 1

        // Linha accent no topo do painel
        Rectangle {
            anchors { top: parent.top; left: parent.left; right: parent.right }
            height: 2
            radius: 12
            color: "#00c853"
        }

        Column {
            anchors {
                fill: parent
                margins: 36
                topMargin: 40
            }
            spacing: 18

            // Avatar
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 68
                height: 68
                radius: 34
                color: "#161b22"
                border.color: "#00c853"
                border.width: 2

                Text {
                    anchors.centerIn: parent
                    text: (userModel.currentUser.realName || userModel.currentUser.name || "U").substring(0, 1).toUpperCase()
                    font.pixelSize: 28
                    font.family: "Noto Sans"
                    font.weight: Font.Medium
                    color: "#00c853"
                }
            }

            // Nome do usuário
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: userModel.currentUser.realName || userModel.currentUser.name || "Usuário"
                color: "#e6edf3"
                font.pixelSize: 15
                font.weight: Font.Medium
                font.family: "Noto Sans"
            }

            // Campo de senha
            TextField {
                id: passwordField
                width: parent.width
                height: 44
                echoMode: TextInput.Password
                placeholderText: "Digite sua senha"
                focus: true
                font.pixelSize: 14
                font.family: "Noto Sans"

                background: Rectangle {
                    color: "#161b22"
                    radius: 8
                    border.color: passwordField.activeFocus ? "#00c853" : "#30363d"
                    border.width: passwordField.activeFocus ? 2 : 1
                    Behavior on border.color { ColorAnimation { duration: 150 } }
                }

                color: "#e6edf3"
                leftPadding: 16
                rightPadding: 16

                Keys.onReturnPressed: sddm.login(
                    userModel.currentUser.name, passwordField.text, sessionIndex)
                Keys.onEnterPressed: sddm.login(
                    userModel.currentUser.name, passwordField.text, sessionIndex)
            }

            // Botão entrar
            Button {
                width: parent.width
                height: 44
                text: "Entrar"
                font.pixelSize: 14
                font.family: "Noto Sans"
                font.weight: Font.Medium

                background: Rectangle {
                    color: parent.pressed ? "#00a040" : (parent.hovered ? "#00e676" : "#00c853")
                    radius: 8
                    Behavior on color { ColorAnimation { duration: 120 } }
                }

                contentItem: Text {
                    text: parent.text
                    color: "#0d1117"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font: parent.font
                }

                onClicked: sddm.login(
                    userModel.currentUser.name, passwordField.text, sessionIndex)
            }

            // Mensagem de erro
            Text {
                id: errorMessage
                width: parent.width
                text: ""
                color: "#f85149"
                font.pixelSize: 12
                font.family: "Noto Sans"
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                visible: text !== ""
            }
        }
    }

    // Barra inferior — sessão + ações de sistema
    Row {
        anchors {
            right: parent.right
            bottom: parent.bottom
            margins: 30
        }
        spacing: 8

        ComboBox {
            id: sessionCombo
            width: 140
            height: 34
            model: sessionModel
            currentIndex: sessionIndex
            textRole: "name"
            font.pixelSize: 12
            font.family: "Noto Sans"
            onCurrentIndexChanged: sessionIndex = currentIndex

            background: Rectangle {
                color: "#161b22"
                radius: 6
                border.color: "#30363d"
                border.width: 1
            }
            contentItem: Text {
                leftPadding: 10
                text: parent.displayText
                color: "#8b949e"
                font: parent.font
                verticalAlignment: Text.AlignVCenter
            }
        }

        // Reiniciar
        Rectangle {
            width: 34; height: 34
            radius: 6
            color: rebootArea.containsMouse ? "#161b22" : "transparent"
            border.color: "#30363d"
            border.width: 1
            Behavior on color { ColorAnimation { duration: 120 } }

            Text {
                anchors.centerIn: parent
                text: "↺"
                font.pixelSize: 18
                color: rebootArea.containsMouse ? "#e6edf3" : "#8b949e"
            }

            MouseArea {
                id: rebootArea
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: sddm.reboot()
            }

            ToolTip.visible: rebootArea.containsMouse
            ToolTip.text: "Reiniciar"
        }

        // Desligar
        Rectangle {
            width: 34; height: 34
            radius: 6
            color: powerArea.containsMouse ? "#1c0a0a" : "transparent"
            border.color: powerArea.containsMouse ? "#f85149" : "#30363d"
            border.width: 1
            Behavior on color { ColorAnimation { duration: 120 } }

            Text {
                anchors.centerIn: parent
                text: "⏻"
                font.pixelSize: 16
                color: powerArea.containsMouse ? "#f85149" : "#8b949e"
            }

            MouseArea {
                id: powerArea
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: sddm.powerOff()
            }

            ToolTip.visible: powerArea.containsMouse
            ToolTip.text: "Desligar"
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            errorMessage.text = "Senha incorreta. Tente novamente."
            passwordField.text = ""
            passwordField.focus = true
        }
    }
}
