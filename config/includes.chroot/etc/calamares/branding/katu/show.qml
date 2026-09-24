/* Katu OS — Calamares Installation Slideshow
   Slides informativos durante a instalação — PT-BR amigável
   Paleta: #0d1117 / #00c853 / #ffab00                        */

import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: slideshow

    property color katuGreen:  "#00c853"
    property color katuAmber:  "#ffab00"
    property color katuBg:     "#0d1117"
    property color katuBgAlt:  "#161b22"
    property color katuText:   "#e6edf3"
    property color katuMuted:  "#8b949e"
    property color katuBorder: "#30363d"
    property color katuLink:   "#58a6ff"

    // Cada slide tem: imagem de fundo + título + descrição
    property var slideData: [
        {
            img:   "slide-01.png",
            titulo: "Bem-vindo ao Katu OS!",
            desc:  "Uma experiência brasileira para estudar, trabalhar e criar."
        },
        {
            img:   "slide-02.png",
            titulo: "Trabalhe com o LibreOffice",
            desc:  "Escreva textos, prepare planilhas e monte apresentações com o LibreOffice."
        },
        {
            img:   "slide-03.png",
            titulo: "Navegue do seu jeito",
            desc:  "Escolha entre Firefox e Google Chrome para acessar seus sites favoritos."
        },
        {
            img:   "slide-04.png",
            titulo: "Tudo em português do Brasil",
            desc:  "Selecione seu idioma, teclado e região durante a instalação."
        },
        {
            img:   "slide-05.png",
            titulo: "Uma base aberta e confiável",
            desc:  "Conheça as opções de privacidade e atualização depois da instalação."
        },
        {
            img:   "slide-06.png",
            titulo: "Seu Katu OS está quase pronto",
            desc:  "Acompanhe a instalação. Ao terminar, reinicie e aproveite o sistema."
        }
    ]

    Rectangle {
        anchors.fill: parent
        color: katuBg

        // Linha accent topo
        Rectangle {
            anchors { top: parent.top; left: parent.left; right: parent.right }
            height: 3
            color: katuGreen
            z: 20
        }

        // Área de imagem (metade superior)
        Item {
            id: areaImagem
            anchors { top: parent.top; left: parent.left; right: parent.right }
            height: parent.height * 0.55

            SwipeView {
                id: swipeView
                anchors.fill: parent
                currentIndex: 0

                Repeater {
                    model: slideData

                    Item {
                        Image {
                            anchors.fill: parent
                            source: modelData.img
                            fillMode: Image.PreserveAspectCrop
                            asynchronous: true
                            smooth: true

                            Rectangle {
                                anchors.fill: parent
                                color: "#0d1117"
                                opacity: 0.40
                            }
                        }
                    }
                }
            }
        }

        // Área de texto (metade inferior)
        Rectangle {
            id: areaTexto
            anchors {
                top: areaImagem.bottom
                left: parent.left
                right: parent.right
                bottom: parent.bottom
            }
            color: katuBg

            Column {
                anchors {
                    fill: parent
                    margins: 36
                    topMargin: 28
                }
                spacing: 12

                // Número do slide
                Text {
                    text: (swipeView.currentIndex + 1) + " / " + slideData.length
                    color: katuGreen
                    font.pixelSize: 12
                    font.family: "Noto Sans"
                    font.letterSpacing: 1
                }

                // Título do slide
                Text {
                    id: tituloSlide
                    width: parent.width
                    text: slideData[swipeView.currentIndex] ? slideData[swipeView.currentIndex].titulo : ""
                    color: katuText
                    font.pixelSize: 22
                    font.family: "Noto Sans"
                    font.weight: Font.Bold
                    wrapMode: Text.WordWrap

                    Behavior on text {
                        SequentialAnimation {
                            NumberAnimation { target: tituloSlide; property: "opacity"; to: 0; duration: 150 }
                            PropertyAction { }
                            NumberAnimation { target: tituloSlide; property: "opacity"; to: 1; duration: 200 }
                        }
                    }
                }

                // Descrição
                Text {
                    id: descSlide
                    width: parent.width
                    text: slideData[swipeView.currentIndex] ? slideData[swipeView.currentIndex].desc : ""
                    color: katuMuted
                    font.pixelSize: 14
                    font.family: "Noto Sans"
                    lineHeight: 1.5
                    wrapMode: Text.WordWrap

                    Behavior on text {
                        SequentialAnimation {
                            NumberAnimation { target: descSlide; property: "opacity"; to: 0; duration: 150 }
                            PropertyAction { }
                            NumberAnimation { target: descSlide; property: "opacity"; to: 1; duration: 200 }
                        }
                    }
                }
            }

            // Indicadores pill na base
            Row {
                anchors {
                    bottom: parent.bottom
                    horizontalCenter: parent.horizontalCenter
                    bottomMargin: 20
                }
                spacing: 8

                Repeater {
                    model: slideData.length

                    Rectangle {
                        width:  swipeView.currentIndex === index ? 32 : 8
                        height: 4
                        radius: 2
                        color:  swipeView.currentIndex === index ? katuGreen : katuBorder
                        Behavior on width { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                        Behavior on color { ColorAnimation { duration: 200 } }
                    }
                }
            }
        }
    }

    // Auto-avanço a cada 7 segundos
    Timer {
        interval: 7000
        running: true
        repeat: true
        onTriggered: {
            var next = swipeView.currentIndex + 1
            swipeView.currentIndex = next < swipeView.count ? next : 0
        }
    }
}
