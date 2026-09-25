// Katu OS SDDM theme: QtQuick 2.0 primitives for Debian 13's Qt 6 greeter.
import QtQuick 2.0
import QtQuick.Window 2.0
import SddmComponents 2.0

Rectangle {
    id: root
    width: Screen.width
    height: Screen.height
    color: "#07130f"
    property int sessionIndex: sessionModel.lastIndex
    readonly property bool compact: width < 1180 || height < 760
    readonly property int inset: Math.max(24, Math.min(width, height) * 0.045)

    function authenticate() {
        if (password.text.length > 0)
            sddm.login(userModel.currentUser.name, password.text, sessionIndex)
    }

    Image {
        anchors.fill: parent
        source: config.background || "background.png"
        fillMode: Image.PreserveAspectCrop
        asynchronous: true
        smooth: true
    }
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#d907130f" }
            GradientStop { position: 0.52; color: "#9907130f" }
            GradientStop { position: 0.78; color: "#3307130f" }
            GradientStop { position: 1.0; color: "#1a07130f" }
        }
    }

    Rectangle {
        x: inset; y: inset; width: 118; height: 3; radius: 2; color: "#d8ad48"
    }
    Image {
        x: inset; y: inset + 17
        width: Math.min(210, root.width * 0.24)
        height: Math.min(60, root.height * 0.09)
        source: "logo.png"; fillMode: Image.PreserveAspectFit
        horizontalAlignment: Image.AlignLeft; smooth: true
    }
    Text {
        x: inset; y: inset + 80
        text: "Livre. Brasileiro. Para todos."
        color: "#f0ecdc"; font.family: "Noto Sans"
        font.pixelSize: root.compact ? 13 : 16
    }

    Column {
        anchors.right: parent.right; anchors.top: parent.top
        anchors.rightMargin: inset; anchors.topMargin: inset; spacing: 2
        Clock {
            anchors.right: parent.right
            timeFont.family: "Noto Sans"; timeFont.pixelSize: root.compact ? 25 : 34
            timeFont.weight: Font.Light; color: "#f0ecdc"
        }
        Text {
            anchors.right: parent.right
            text: Qt.formatDate(new Date(), "dddd, d 'de' MMMM")
            color: "#d0d8ce"; font.family: "Noto Sans"; font.pixelSize: 12
        }
    }

    Rectangle {
        id: panel
        width: Math.min(390, root.width * (root.compact ? 0.82 : 0.31))
        height: Math.min(470, root.height - inset * 2)
        x: inset; y: Math.max(inset + 112, (root.height - height) / 2)
        color: "#e607130f"; radius: 16
        border.color: "#66f0ecdc"; border.width: 1

        Image {
            id: mark
            anchors.top: parent.top; anchors.topMargin: 22
            anchors.horizontalCenter: parent.horizontalCenter
            width: 156; height: 48; source: "logo.png"
            fillMode: Image.PreserveAspectFit; smooth: true
        }
        Text {
            id: greeting
            anchors.top: mark.bottom; anchors.topMargin: 12
            anchors.left: parent.left; anchors.right: parent.right
            anchors.leftMargin: 24; anchors.rightMargin: 24
            text: userModel.currentUser.realName || userModel.currentUser.name || "Bem-vindo"
            color: "#f0ecdc"; font.family: "Noto Sans"
            font.pixelSize: 19; font.weight: Font.DemiBold
            horizontalAlignment: Text.AlignHCenter; elide: Text.ElideRight
        }
        Text {
            id: helper
            anchors.top: greeting.bottom; anchors.topMargin: 5
            anchors.left: parent.left; anchors.right: parent.right
            text: "Entre para continuar"; color: "#c8d3c9"
            font.family: "Noto Sans"; font.pixelSize: 13
            horizontalAlignment: Text.AlignHCenter
        }

        Rectangle {
            id: passwordBox
            anchors.top: helper.bottom; anchors.topMargin: 20
            anchors.left: parent.left; anchors.right: parent.right
            anchors.leftMargin: 28; anchors.rightMargin: 28
            height: 48; color: "#e607130f"; radius: 8
            border.color: password.activeFocus ? "#ffcc55" : "#668b9888"
            border.width: password.activeFocus ? 2 : 1
            TextInput {
                id: password
                anchors.fill: parent; anchors.leftMargin: 14; anchors.rightMargin: 14
                echoMode: TextInput.Password; color: "#f0ecdc"
                selectionColor: "#447c6d"; selectedTextColor: "#ffffff"
                font.family: "Noto Sans"; font.pixelSize: 14
                verticalAlignment: TextInput.AlignVCenter; focus: true
                Keys.onReturnPressed: root.authenticate()
                Keys.onEnterPressed: root.authenticate()
                Text {
                    anchors.fill: parent; text: "Senha"; color: "#b7c2b8"
                    font: password.font; verticalAlignment: Text.AlignVCenter
                    visible: !password.text && !password.activeFocus
                }
            }
        }
        Rectangle {
            id: submit
            anchors.top: passwordBox.bottom; anchors.topMargin: 12
            anchors.left: passwordBox.left; anchors.right: passwordBox.right
            height: 48; radius: 8
            color: submitMouse.pressed ? "#a87932" : submitMouse.containsMouse ? "#ffcf62" : "#d8ad48"
            Text {
                anchors.centerIn: parent; text: "Entrar"; color: "#101810"
                font.family: "Noto Sans"; font.pixelSize: 14; font.weight: Font.DemiBold
            }
            MouseArea {
                id: submitMouse; anchors.fill: parent; hoverEnabled: true
                onClicked: root.authenticate()
            }
        }
        Text {
            id: errorMessage
            anchors.top: submit.bottom; anchors.topMargin: 8
            anchors.left: passwordBox.left; anchors.right: passwordBox.right
            text: ""; color: "#ff9c91"; font.family: "Noto Sans"
            font.pixelSize: 12; wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter; visible: text.length > 0
        }
        ComboBox {
            id: session
            anchors.left: passwordBox.left; anchors.right: passwordBox.right
            anchors.bottom: parent.bottom; anchors.bottomMargin: 23
            model: sessionModel; index: sessionIndex; arrowIcon: "angle-down.png"
            onIndexChanged: sessionIndex = index
        }
    }

    Row {
        anchors.right: parent.right; anchors.bottom: parent.bottom
        anchors.rightMargin: inset; anchors.bottomMargin: inset; spacing: 10
        Rectangle {
            width: 48; height: 44; radius: 8
            color: rebootMouse.containsMouse ? "#55776666" : "#2207130f"
            border.color: "#55776666"
            Text { anchors.centerIn: parent; text: "↻"; color: "#f0ecdc"; font.pixelSize: 20 }
            MouseArea { id: rebootMouse; anchors.fill: parent; hoverEnabled: true; onClicked: sddm.reboot() }
        }
        Rectangle {
            width: 48; height: 44; radius: 8
            color: powerMouse.containsMouse ? "#55c85c55" : "#2207130f"
            border.color: "#55776666"
            Text { anchors.centerIn: parent; text: "⏻"; color: "#f0ecdc"; font.pixelSize: 19 }
            MouseArea { id: powerMouse; anchors.fill: parent; hoverEnabled: true; onClicked: sddm.powerOff() }
        }
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            errorMessage.text = "Senha incorreta. Tente novamente."
            password.text = ""
            password.focus = true
        }
    }
}
