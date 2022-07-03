class Figure {
    constructor(id, config) {
        this.config = config
        let canvas = document.getElementById(id)
        canvas.setAttribute("width", config.size)
        canvas.setAttribute("height", config.size)

        this.img = canvas.getContext("2d")
        this.canvas = canvas
        this.stack = []
        this.load_image()
    }

    add_listener (listener) {
        this.canvas.addEventListener("click", (event) => {
            let { offsetX, offsetY, ctrlKey, shiftKey } = event
            let { margin, size } = this.config
            let block_size = Math.floor((size - 2 * margin) / 8)
            let col = Math.floor((offsetX - margin) / block_size) + 1
            let row = 9 - (Math.floor((offsetY - margin) / block_size) + 1)
            if ((col >= 1 && col <= 8) && (row >= 1 && row <= 8)) {
                listener([col, row], ctrlKey, shiftKey)
            }
        })
    }

    draw_chessboard () {
        this.img.save()
        let {
            margin, size,
            border_width,
            white_block_color,
            black_block_color } = this.config

        this.img.lineWidth = border_width
        this.img.strokeRect(margin, margin, size - 2 * margin, size - 2 * margin)

        let block_size = Math.floor((size - 2 * margin) / 8)
        for (let i = 0; i < 8; i++) {
            for (let j = 0; j < 8; j++) {
                if ((i + j) % 2 == 0) {
                    this.img.fillStyle = `rgb(${white_block_color})`
                }
                else {
                    this.img.fillStyle = `rgb(${black_block_color})`
                }
                this.img.fillRect(margin + i * block_size, margin + j * block_size, block_size, block_size)
                if (i == 0) {
                    this.img.fillStyle = '#6ac8ff'
                    this.img.font = '8px Frutiger'
                    this.img.fillText(8 - j, margin + 2, margin + j * block_size + 8)
                }
                if (j == 7) {
                    this.img.fillStyle = '#6ac8ff'
                    this.img.font = '8px Frutiger'
                    this.img.fillText(String.fromCharCode('A'.charCodeAt() + i), margin + (i + 1) * block_size - 8, margin + (j + 1) * block_size - 2)
                }
            }
        }
        this.img.restore()
        return this
    }

    load_image () {
        let pieces = [
            'white_king',
            'white_queen',
            'white_rook',
            'white_bishop',
            'white_knight',
            'white_pawn',
            'black_king',
            'black_queen',
            'black_rook',
            'black_bishop',
            'black_knight',
            'black_pawn'
        ]
        this.pieces = {}
        for (let key of pieces) {
            let image = new Image()
            image.onload = () => {
                this.pieces[key] = image
            }
            image.src = `../../${key}.png`
        }
    }

    draw_chess_pieces (data) {
        this.img.save()
        let {
            margin, size,
            blood_color, blood_width
        } = this.config

        let block_size = Math.floor((size - 2 * margin) / 8)

        for (let i = 0; i < 8; i++) {
            for (let j = 0; j < 8; j++) {
                let piece = data[`${i + 1}${j + 1}`]
                if (piece) {
                    let [color, name, probability] = piece

                    let draw_a_piece = (image) => {
                        this.img.save()
                        this.img.drawImage(
                            image,
                            margin + i * block_size,
                            margin + (7 - j) * block_size,
                            block_size,
                            block_size
                        )
                        if (probability != 1) {
                            this.img.strokeStyle = `rgb(${blood_color})`
                            this.img.lineWidth = blood_width
                            this.img.beginPath()
                            this.img.arc(
                                margin + (i + 0.5) * block_size,
                                margin + (7 - j + 0.5) * block_size,
                                block_size / 2 - 2,
                                (0.5 - probability) * Math.PI,
                                Math.PI - (0.5 - probability) * Math.PI
                            )
                            this.img.stroke()
                        }
                        this.img.restore()
                    }

                    let image = this.pieces[`${color}_${name}`]
                    if (image) {
                        draw_a_piece(image)
                    } else {
                        let id = setInterval(() => {
                            let image = this.pieces[`${color}_${name}`]
                            if (image) {
                                draw_a_piece(image)
                                clearInterval(id)
                            }
                        }, 100)
                    }
                }

            }
        }
        this.stack.push(data)
        this.img.restore()
        return this
    }

    draw (data) {
        this.draw_chessboard()
        if (data) {
            this.draw_chess_pieces(data)
        }
        return this
    }

    clear () {
        let { size } = this.config
        this.img.clearRect(0, 0, size, size)
        return this
    }

    reload () {
        this.clear()
        this.draw(this.stack.slice(-1)[0])
        return this
    }

    back () {
        if (this.stack.length > 1) {
            this.stack.pop()
            this.reload()
        }
        return this
    }

    checked (blocks) {
        if (this.stack.length == 0) {
            return
        }
        this.img.save()
        this.reload()
        let {
            margin, size, thickness
        } = this.config

        let block_size = Math.floor((size - 2 * margin) / 8)

        for (let [place, color] of blocks) {
            this.img.strokeStyle = `rgb(${color})`
            this.img.lineWidth = thickness

            this.img.strokeRect(
                margin + (place[0] - 1) * block_size + 2,
                margin + (8 - place[1]) * block_size + 2,
                block_size - 4,
                block_size - 4
            )
        }
        this.img.restore()
        return this
    }

    drag (handler, disabled) {
        this.canvas.onmousedown = (event) => {
            if (disabled()) {
                return
            }
            let { offsetX, offsetY } = event
            let { margin, size } = this.config
            let block_size = Math.floor((size - 2 * margin) / 8)
            let col = Math.floor((offsetX - margin) / block_size) + 1
            let row = 9 - (Math.floor((offsetY - margin) / block_size) + 1)

            if ((col >= 1 && col <= 8) && (row >= 1 && row <= 8)
                && this.stack.length > 0 && this.stack.slice(-1)[0][`${col}${row}`]) {

                let chessboard = this.stack.pop()
                let [color, name, probability] = chessboard[`${col}${row}`]
                delete chessboard[`${col}${row}`]
                this.stack.push(chessboard)
                this.canvas.onmousemove = (event) => {
                    this.reload()
                    let x = event.offsetX
                    let y = event.offsetY
                    if (x <= block_size / 4 || x + block_size / 4 >= this.canvas.width ||
                        y <= block_size / 4 || y + block_size / 4 >= this.canvas.height) {
                        this.canvas.onmousemove = null
                        this.canvas.onmouseup = null
                        handler(color, name)

                    } else {
                        let image = this.pieces[`${color}_${name}`]
                        this.img.drawImage(image, x - block_size / 2, y - block_size / 2, block_size, block_size)
                    }
                }

                this.canvas.onmouseup = (event) => {
                    this.canvas.onmousemove = null
                    this.canvas.onmouseup = null

                    col = Math.floor((event.offsetX - margin) / block_size) + 1
                    row = 9 - (Math.floor((event.offsetY - margin) / block_size) + 1)
                    if ((col >= 1 && col <= 8) && (row >= 1 && row <= 8)) {
                        chessboard = this.stack.pop()
                        let old_piece = chessboard[`${col}${row}`]
                        if (old_piece) {
                            handler(old_piece[0], old_piece[1])
                        }
                        chessboard[`${col}${row}`] = [color, name, probability]
                        this.stack.push(chessboard)
                    }
                }
            }
        }
    }

    init () {
        this.stack = []
        this.draw_chessboard()
    }
}

export default Figure
