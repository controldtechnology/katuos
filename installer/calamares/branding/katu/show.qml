/* Katu OS — Calamares Installation Slides */

import QtQuick 2.15
import QtQuick.Controls 2.15
import Calamares 1.0 as Calamares

Calamares.Slideshow {
    id: slideshow

    // Slides como imagens PNG (geradas pelo Katu OS Visual Pack)
    property var slides: [
        "slide-01.png",
        "slide-02.png",
        "slide-03.png",
        "slide-04.png",
        "slide-05.png",
        "slide-06.png"
    ]

    property color katuGreen: "#2ecc71"

    Rectangle {
        anchors.fill: parent
        color: "#1a1a1a"

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
