// Katu OS — slideshow editorial. Mantém ordem, intervalo e imagens do branding.
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: slideshow
    property var slideData: [
        { img: "slide-01.png", alt: "Katu OS — tecnologia brasileira feita para todos." },
        { img: "slide-02.png", alt: "Um sistema livre para trabalhar e criar." },
        { img: "slide-03.png", alt: "Uma experiência familiar e intuitiva." },
        { img: "slide-04.png", alt: "Personalize o sistema do seu jeito." },
        { img: "slide-05.png", alt: "Inspirado pelo Brasil: natureza e tecnologia." },
        { img: "slide-06.png", alt: "Katu OS está sendo preparado." }
    ]

    Rectangle {
        anchors.fill: parent
        color: "#001111"
    }

    SwipeView {
        id: swipeView
        anchors.fill: parent
        anchors.margins: Math.max(8, Math.min(parent.width, parent.height) * 0.035)
        currentIndex: 0
        clip: true
        interactive: false

        Repeater {
            model: slideData
            Item {
                Image {
                    id: slideImage
                    anchors.fill: parent
                    source: modelData.img
                    fillMode: Image.PreserveAspectFit
                    asynchronous: true
                    cache: true
                    smooth: true
                    sourceSize.width: parent.width
                    sourceSize.height: parent.height
                    opacity: SwipeView.isCurrentItem ? 1.0 : 0.72
                    Behavior on opacity { NumberAnimation { duration: 220 } }
                    Accessible.name: modelData.alt
                }
            }
        }
    }

    Row {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 5
        spacing: 7
        Repeater {
            model: slideData.length
            Rectangle {
                width: swipeView.currentIndex === index ? 22 : 6
                height: 3
                radius: 2
                color: swipeView.currentIndex === index ? "#DDAA44" : "#66887766"
                Behavior on width { NumberAnimation { duration: 180 } }
            }
        }
    }

    Timer {
        interval: 7000
        running: true
        repeat: true
        onTriggered: swipeView.currentIndex = (swipeView.currentIndex + 1) % slideData.length
    }
}
