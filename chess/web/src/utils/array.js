Array.prototype.equals = function (array) {
    // if the other array is a falsy value, return
    if (!array)
        return false;

    // compare lengths - can save a lot of time
    if (this.length != array.length)
        return false;

    for (var i = 0, l = this.length; i < l; i++) {
        // Check if we have nested arrays
        if (this[i] instanceof Array && array[i] instanceof Array) {
            // recurse into the nested arrays
            if (!this[i].equals(array[i]))
                return false;
        }
        else if (this[i] != array[i]) {
            return false;
        }
    }
    return true;
}

Array.prototype.contain = function (array) {
    if (this.length < array.length) {
        return false
    }

    let count = 0
    for (let a of array) {
        for (let b of this) {
            if (a.equals(b)) {
                count++
                break
            }
        }
    }
    return count == array.length
}

Array.prototype.minus = function (array) {
    let index = []
    for (let i = 0; i < this.length; i++) {
        if (array.contain([this[i]])) {
            index.push(i)
        }
    }
    let data = []
    for (let i = 0; i < this.length; i++) {
        if (index.indexOf(i) < 0) {
            data.push(this[i])
        }
    }
    return data
}
