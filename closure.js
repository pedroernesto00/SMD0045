function makeObj(x) {
    var name = x;
    var obj = {};
    
    function displayName() {
        console.log(name)
    }

    obj.name = displayName;
    return obj;
}


a = makeObj('Cadeira');
a.name();