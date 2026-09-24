// Katu OS — SDDM responsivo. Autenticação e ações permanecem no SDDM.
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: Screen.width
    height: Screen.height
    color: "#001111"
    property int sessionIndex: sessionModel.lastIndex
    readonly property bool compact: width < 1180 || height < 760
    readonly property int safeInset: Math.max(24, Math.min(width, height) * 0.045)

    Image {
        anchors.fill: parent
        source: config.background || "background.png"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        cache: true
    }
    // Escurecimento localizado mantém a arte visível à direita e dá contraste ao login.
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#e6001111" }
            GradientStop { position: 0.43; color: "#99001111" }
            GradientStop { position: 0.72; color: "#26001111" }
            GradientStop { position: 1.0; color: "#18001111" }
        }
    }
    Rectangle {
        width: parent.width * 0.22
        height: 2
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: safeInset
        anchors.topMargin: safeInset
        color: "#DDAA44"
    }

    Column {
        id: identity
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.leftMargin: safeInset
        anchors.topMargin: safeInset + 14
        spacing: 10
        Image {
            source: "logo.png"
            width: Math.min(root.width * 0.24, 250)
            height: Math.min(root.height * 0.1, 68)
            fillMode: Image.PreserveAspectFit
            horizontalAlignment: Image.AlignLeft
            smooth: true
        }
        Text {
            text: "Livre. Brasileiro. Para todos."
            color: "#EEEEDD"
            font.family: "Noto Sans"
            font.pixelSize: root.compact ? 13 : 16
        }
    }

    Column {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.rightMargin: safeInset
        anchors.topMargin: safeInset
        spacing: 3
        Clock {
            anchors.right: parent.right
            timeFont.family: "Noto Sans"
            timeFont.pixelSize: root.compact ? 24 : 32
            timeFont.weight: Font.Light
            color: "#EEEEDD"
        }
        Text {
            anchors.right: parent.right
            text: Qt.formatDate(new Date(), "dddd, d 'de' MMMM")
            color: "#C8D3C9"
            font.family: "Noto Sans"
            font.pixelSize: 12
        }
    }

    Rectangle {
        id: loginPanel
        width: Math.min(390, root.width * (root.compact ? 0.82 : 0.31))
        height: Math.min(462, root.height - safeInset * 2)
        anchors.left: parent.left
        anchors.leftMargin: safeInset
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: root.compact ? 18 : 0
        color: "#E6001111"
        radius: 16
        border.color: "#66EEEEDD"
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: root.compact ? 22 : 30
            spacing: 14
            Image {
                source: "logo.png"
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 176
                Layout.preferredHeight: 52
                fillMode: Image.PreserveAspectFit
            }
            Text {
                Layout.fillWidth: true
                text: userModel.currentUser.realName || userModel.currentUser.name || "Bem-vindo"
                color: "#EEEEDD"
                font.family: "Noto Sans"
                font.pixelSize: 19
                font.weight: Font.DemiBold
                horizontalAlignment: Text.AlignHCenter
                elide: Text.ElideRight
            }
            Text {
                Layout.fillWidth: true
                text: "Entre para continuar"
                color: "#C8D3C9"
                font.family: "Noto Sans"
                font.pixelSize: 13
                horizontalAlignment: Text.AlignHCenter
            }
            TextField {
                id: passwordField
                Layout.fillWidth: true
                Layout.preferredHeight: 48
                echoMode: TextInput.Password
                placeholderText: "Senha"
                focus: true
                color: "#EEEEDD"
                font.family: "Noto Sans"
                font.pixelSize: 14
                leftPadding: 16
                rightPadding: 16
                background: Rectangle {
                    color: "#E6001111"
                    radius: 8
                    border.color: passwordField.activeFocus ? "#FFCC55" : "#55776666"
                    border.width: passwordField.activeFocus ? 2 : 1
                }
                Keys.onReturnPressed: sddm.login(userModel.currentUser.name, passwordField.text, sessionIndex)
                Keys.onEnterPressed: sddm.login(userModel.currentUser.name, passwordField.text, sessionIndex)
            }
            Button {
                Layout.fillWidth: true
                Layout.preferredHeight: 48
                text: "Entrar"
                font.family: "Noto Sans"
                font.pixelSize: 14
                font.weight: Font.DemiBold
                background: Rectangle {
                    radius: 8
                    color: parent.pressed ? "#AA7733" : (parent.hovered ? "#FFCC55" : "#DDAA44")
                }
                contentItem: Text {
                    text: parent.text
                    color: "#001111"
                    font: parent.font
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: sddm.login(userModel.currentUser.name, passwordField.text, sessionIndex)
            }
            Text {
                id: errorMessage
                Layout.fillWidth: true
                text: ""
                color: "#FF9C91"
                font.family: "Noto Sans"
                font.pixelSize: 12
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                visible: text !== ""
            }
            Item { Layout.fillHeight: true }
            RowLayout {
                Layout.fillWidth: true
                ComboBox {
                    id: sessionCombo
                    Layout.fillWidth: true
                    model: sessionModel
                    currentIndex: sessionIndex
                    textRole: "name"
                    onCurrentIndexChanged: sessionIndex = currentIndex
                    background: Rectangle { color: "#66001111"; radius: 7; border.color: "#55776666" }
                    contentItem: Text {
                        leftPadding: 12
                        text: sessionCombo.displayText
                        color: "#EEEEDD"
                        font.family: "Noto Sans"
                        font.pixelSize: 12
                        verticalAlignment: Text.AlignVCenter
                        elide: Text.ElideRight
                    }
                }
                Button {
                    text: "↻"
                    implicitWidth: 44; implicitHeight: 42
                    onClicked: sddm.reboot()
                    background: Rectangle { color: parent.hovered ? "#55776666" : "#22001111"; radius: 7; border.color: "#55776666" }
                    contentItem: Text { text: parent.text; color: "#EEEEDD"; font.pixelSize: 18; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    ToolTip.text: "Reiniciar"; ToolTip.visible: hovered
                }
                Button {
                    text: "⏻"
                    implicitWidth: 44; implicitHeight: 42
                    onClicked: sddm.powerOff()
                    background: Rectangle { color: parent.hovered ? "#55C85C55" : "#22001111"; radius: 7; border.color: "#55776666" }
                    contentItem: Text { text: parent.text; color: "#EEEEDD"; font.pixelSize: 17; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    ToolTip.text: "Desligar"; ToolTip.visible: hovered
                }
            }
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
