// Katu OS SDDM Theme
// Livre. Brasileiro. Para todos.

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#1a1a1a"

    // Propriedades injetadas pelo SDDM
    property int sessionIndex: sessionModel.lastIndex
    property bool isLive: false

    // Fundo — wallpaper Katu
    Image {
        id: background
        anchors.fill: parent
        source: config.background || "background.jpg"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        cache: false
    }

    // Overlay escuro sobre wallpaper
    Rectangle {
        anchors.fill: parent
        color: "#000000"
        opacity: 0.55
    }

    // Marca d'água Katu (canto inferior esquerdo)
    Column {
        anchors {
            left: parent.left
            bottom: parent.bottom
            margins: 40
        }
        spacing: 4

        Image {
            id: logoKatu
            source: "logo.svg"
            width: 120
            height: 48
            fillMode: Image.PreserveAspectFit
            smooth: true
        }

        Text {
            text: "Livre. Brasileiro. Para todos."
            font.pixelSize: 11
            color: "#88ffffff"
            font.family: "Noto Sans"
        }
    }

    // Relógio (canto superior direito)
    Column {
        anchors {
            right: parent.right
            top: parent.top
            margins: 40
        }
        spacing: 2

        Clock {
            id: clock
            anchors.horizontalCenter: parent.horizontalCenter
        }
    }

    // Painel central de login
    Rectangle {
        id: loginPanel
        anchors.centerIn: parent
        width: 380
        height: 440
        color: "#cc1a1a1a"
        radius: 16
        border.color: "#2a2a2a"
        border.width: 1

        layer.enabled: true
        layer.effect: null

        Column {
            anchors {
                fill: parent
                margins: 36
            }
            spacing: 20

            // Avatar/ícone do usuário
            Image {
                anchors.horizontalCenter: parent.horizontalCenter
                source: userModel.currentUser.icon || "user.svg"
                width: 72
                height: 72
                fillMode: Image.PreserveAspectCrop

                Rectangle {
                    anchors.fill: parent
                    radius: width / 2
                    color: "transparent"
                    border.color: "#2ecc71"
                    border.width: 2
                }
            }

            // Nome do usuário
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: userModel.currentUser.realName || userModel.currentUser.name || "Usuário"
                color: "#f8f9fa"
                font.pixelSize: 16
                font.weight: Font.Medium
                font.family: "Noto Sans"
            }

            // Campo de senha
            TextField {
                id: passwordField
                width: parent.width
                height: 44
                echoMode: TextInput.Password
                placeholderText: "Senha"
                focus: true
                font.pixelSize: 14
                font.family: "Noto Sans"

                background: Rectangle {
                    color: "#2a2a2a"
                    radius: 8
                    border.color: passwordField.activeFocus ? "#2ecc71" : "#3a3a3a"
                    border.width: 1
                }

                color: "#f8f9fa"
                leftPadding: 16
                rightPadding: 16

                Keys.onReturnPressed: sddm.login(
                    userModel.currentUser.name,
                    passwordField.text,
                    sessionIndex
                )
                Keys.onEnterPressed: sddm.login(
                    userModel.currentUser.name,
                    passwordField.text,
                    sessionIndex
                )
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
                    color: parent.pressed ? "#1a5c2a" : (parent.hovered ? "#27ae60" : "#2ecc71")
                    radius: 8
                    Behavior on color { ColorAnimation { duration: 150 } }
                }

                contentItem: Text {
                    text: parent.text
                    color: "#ffffff"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font: parent.font
                }

                onClicked: sddm.login(
                    userModel.currentUser.name,
                    passwordField.text,
                    sessionIndex
                )
            }

            // Mensagem de erro
            Text {
                id: errorMessage
                width: parent.width
                text: ""
                color: "#e74c3c"
                font.pixelSize: 12
                font.family: "Noto Sans"
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                visible: text !== ""
            }
        }
    }

    // Ações de sistema (canto inferior direito)
    Row {
        anchors {
            right: parent.right
            bottom: parent.bottom
            margins: 30
        }
        spacing: 12

        // Sessão
        ComboBox {
            id: sessionCombo
            width: 130
            height: 36
            model: sessionModel
            currentIndex: sessionIndex
            textRole: "name"
            font.pixelSize: 12
            font.family: "Noto Sans"
            onCurrentIndexChanged: sessionIndex = currentIndex

            background: Rectangle {
                color: "#2a2a2a"
                radius: 6
                border.color: "#3a3a3a"
            }
            contentItem: Text {
                leftPadding: 10
                text: parent.displayText
                color: "#f8f9fa"
                font: parent.font
                verticalAlignment: Text.AlignVCenter
            }
        }

        // Reiniciar
        Button {
            width: 36
            height: 36
            text: "↺"
            font.pixelSize: 18
            onClicked: sddm.reboot()
            background: Rectangle {
                color: parent.hovered ? "#333333" : "#2a2a2a"
                radius: 6
            }
            contentItem: Text {
                text: parent.text
                color: "#aaaaaa"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font: parent.font
            }
            ToolTip.visible: hovered
            ToolTip.text: "Reiniciar"
        }

        // Desligar
        Button {
            width: 36
            height: 36
            text: "⏻"
            font.pixelSize: 16
            onClicked: sddm.powerOff()
            background: Rectangle {
                color: parent.hovered ? "#333333" : "#2a2a2a"
                radius: 6
            }
            contentItem: Text {
                text: parent.text
                color: "#aaaaaa"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font: parent.font
            }
            ToolTip.visible: hovered
            ToolTip.text: "Desligar"
        }
    }

    // Conexões com SDDM
    Connections {
        target: sddm
        function onLoginFailed() {
            errorMessage.text = "Senha incorreta. Tente novamente."
            passwordField.text = ""
            passwordField.focus = true
        }
    }
}
