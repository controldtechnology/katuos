/* Katu OS — Calamares Installation Slideshow
   Amazônia Dark: #0d1117 / #00c853 / #ffab00  */

import QtQuick 2.15
import QtQuick.Controls 2.15
import Calamares 1.0 as Calamares

Calamares.Slideshow {
    id: slideshow

    property color katuGreen:  "#00c853"
    property color katuAmber:  "#ffab00"
    property color katuBg:     "#0d1117"
    property color katuBgAlt:  "#161b22"
    property color katuText:   "#e6edf3"
    property color katuMuted:  "#8b949e"
    property color katuBorder: "#30363d"

    property var slides: [
        "slide-01.png",
        "slide-02.png",
        "slide-03.png",
        "slide-04.png",
        "slide-05.png",
        "slide-06.png"
    ]

    Rectangle {
        anchors.fill: parent
        color: katuBg

        // Linha accent topo
        Rectangle {
            anchors { top: parent.top; left: parent.left; right: parent.right }
            height: 2
            color: katuGreen
            z: 10
        }

        SwipeView {
            id: swipeView
            anchors.fill: parent
            currentIndex: 0

            Repeater {
                model: slides

                Item {
                    Image {
                        anchors.fill: parent
                        source: modelData
                        fillMode: Image.PreserveAspectCrop
                        asynchronous: true
                        smooth: true

                        // Overlay suave nos slides
                        Rectangle {
                            anchors.fill: parent
                            color: "#0d1117"
                            opacity: 0.35
                        }
                    }
                }
            }
        }

        // Indicadores de slide
        Row {
            anchors {
                bottom: parent.bottom
                horizontalCenter: parent.horizontalCenter
                bottomMargin: 24
            }
            spacing: 8

            Repeater {
                model: slides.length

                Rectangle {
                    width:  swipeView.currentIndex === index ? 28 : 8
                    height: 4
                    radius: 2
                    color:  swipeView.currentIndex === index ? katuGreen : katuBorder
                    Behavior on width { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                    Behavior on color { ColorAnimation { duration: 200 } }
                }
            }
        }
    }

    // Auto-avanço a cada 6 segundos
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
