// Katu OS SDDM Theme — Amazônia Dark
// Livre. Brasileiro. Para todos.

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import SddmComponents 2.0

Rectangle {
    id: root
    // Follow the active display; fixed 1920x1080 roots clip login controls on VM/laptop screens.
    width: Screen.width
    height: Screen.height
    property color backgroundPrimary: "#041F16"
    property color surfacePrimary: "#063723"
    property color borderDefault: "#326149"
    property color textPrimary: "#F4F1E2"
    property color textMuted: "#C2CBBF"
    property color accentPrimary: "#E0B146"
    property color accentHover: "#F0CC6C"
    property color accentActive: "#B78D2F"
    property color statusError: "#FF6B6B"
    color: backgroundPrimary

    property int sessionIndex: sessionModel.lastIndex
    property int edgeInset: Math.max(24, Math.round(Math.min(width, height) * 0.04))

    // Fundo — wallpaper Katu Amazônia
    Image {
        id: background
        anchors.fill: parent
        source: config.background || "background.png"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        cache: false
    }

    // Overlay escuro — mantém legibilidade
    Rectangle {
        anchors.fill: parent
        color: root.backgroundPrimary
        opacity: 0.36
    }

    // Linha accent verde no topo
    Rectangle {
        anchors { top: parent.top; left: parent.left; right: parent.right }
        height: 2
        color: "#0F7B43"
        opacity: 0.8
    }

    // Logo + tagline (canto inferior esquerdo)
    Column {
        anchors {
            left: parent.left
            bottom: parent.bottom
            leftMargin: root.edgeInset
            bottomMargin: root.edgeInset
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
            color: root.textMuted
            font.family: "Noto Sans"
            font.letterSpacing: 0.5
        }
    }

    // Relógio (canto superior direito)
    Column {
        anchors {
            right: parent.right
            top: parent.top
            topMargin: root.edgeInset
            rightMargin: root.edgeInset
        }
        spacing: 2

        Clock {
            id: clock
            anchors.horizontalCenter: parent.horizontalCenter
            timeFont.pixelSize: 42
            timeFont.family: "Noto Sans"
            timeFont.weight: Font.Light
            color: root.textPrimary
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatDate(new Date(), "dddd, d 'de' MMMM")
            font.pixelSize: 13
            color: root.textMuted
            font.family: "Noto Sans"
        }
    }

    // Painel central de login
    Rectangle {
        id: loginPanel
        anchors.centerIn: parent
        width: Math.min(360, root.width - root.edgeInset * 2)
        height: Math.min(420, root.height - root.edgeInset * 2)
        color: "#F2041F16"
        radius: 12
        border.color: root.borderDefault
        border.width: 1

        // Linha accent no topo do painel
        Rectangle {
            anchors { top: parent.top; left: parent.left; right: parent.right }
            height: 2
            radius: 12
                color: root.accentPrimary
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
                color: root.surfacePrimary
                border.color: root.accentPrimary
                border.width: 2

                Text {
                    anchors.centerIn: parent
                    text: (userModel.currentUser.realName || userModel.currentUser.name || "U").substring(0, 1).toUpperCase()
                    font.pixelSize: 28
                    font.family: "Noto Sans"
                    font.weight: Font.Medium
                    color: root.textPrimary
                }
            }

            // Nome do usuário
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: userModel.currentUser.realName || userModel.currentUser.name || "Usuário"
                color: root.textPrimary
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
                    color: root.surfacePrimary
                    radius: 8
                    border.color: passwordField.activeFocus ? root.accentPrimary : root.borderDefault
                    border.width: passwordField.activeFocus ? 2 : 1
                    Behavior on border.color { ColorAnimation { duration: 150 } }
                }

                color: root.textPrimary
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
                    color: parent.pressed ? root.accentActive : (parent.hovered ? root.accentHover : root.accentPrimary)
                    radius: 8
                    Behavior on color { ColorAnimation { duration: 120 } }
                }

                contentItem: Text {
                    text: parent.text
                    color: root.backgroundPrimary
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
                color: root.statusError
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
            rightMargin: root.edgeInset
            bottomMargin: root.edgeInset
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
                color: root.surfacePrimary
                radius: 6
                border.color: root.borderDefault
                border.width: 1
            }
            contentItem: Text {
                leftPadding: 10
                text: parent.displayText
                color: root.textMuted
                font: parent.font
                verticalAlignment: Text.AlignVCenter
            }
        }

        // Reiniciar
        Rectangle {
            width: 34; height: 34
            radius: 6
            color: rebootArea.containsMouse ? root.surfacePrimary : "transparent"
            border.color: root.borderDefault
            border.width: 1
            Behavior on color { ColorAnimation { duration: 120 } }

            Text {
                anchors.centerIn: parent
                text: "↺"
                font.pixelSize: 18
                color: rebootArea.containsMouse ? root.textPrimary : root.textMuted
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
            border.color: powerArea.containsMouse ? root.statusError : root.borderDefault
            border.width: 1
            Behavior on color { ColorAnimation { duration: 120 } }

            Text {
                anchors.centerIn: parent
                text: "⏻"
                font.pixelSize: 16
                color: powerArea.containsMouse ? root.statusError : root.textMuted
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
