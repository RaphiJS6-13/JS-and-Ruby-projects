
function Class(struct) {
    this.vars = {};
    this.getters = [];
    this.setters = [];
    struct.forEach(function(item){
        if ("init" in item)
        {
            if (Object.keys(item).length > 1) {
                delete item.init;
                throw new SyntaxError('Unexpected excess key-value pair(s) "' + String(Object.keys(item)) + '".');
            }
            this.base = item.init;
        }
        else if ("extends" in item)
        {
            this.extend = item.extends;
        }
        else if ("get" in item) {
            this.getters.push(item);
        }
        else if ("set" in item) {
            this.setters.push(item);
        }
        else if ("private" in item)
        {
            if ("equals" in item) {
                this.vars[item.private] = {private: item.equals};
            }
            else {
                this.vars[item.private] = {private: undefined};
            }
        }
        else if ("public" in item)
        {
            if ("equals" in item) {
                this.vars[item.public] = {public: item.equals};
            }
            else {
                this.vars[item.public] = {public: undefined};
            }
        }
    });
    
    var base;
    if (this.base) {
        base = this.base;
    }
    else
        base = function() {};
    var extend = this.extend;
    var vars = this.vars;
    var setters = this.setters;
    var getters = this.getters;
    function klass() {
        var self = vars;
        function setter(key) {
            return function(item) {
                self[key] = item;
            };
        }
        function getter(key) {
            return function() {
                return self[key];
            };
        }
        for(var key in self) {
            if ("public" in self[key] ) {
                self[key] = self[key].public;
                Object.defineProperty(this, key, {
                    get: getter(key),
                    set: setter(key)
                });
                this[key] = self[key];
            }
            else {
                self[key] = self[key].private;
                if (typeof self[key] === "function") {
                    (function(){
                        var x = {};
                        Object.defineProperty(x, key, {
                            value: self[key]
                        });
                         
                    })();
                }
            }
        }
        var bigger = getters.length > setters.length ? getters.length : setters.length;
        for(var i = 0; i < bigger; i++) {
            var g_now = getters[i];
            var s_now = setters[i];
            if (s_now && g_now && g_now.get === s_now.set){
                Object.defineProperty(this, g_now.get, {
                    get: function() {
                        return g_now.do(self);
                    },
                    set: function(item) {
                        return s_now.do(self, item);
                    }
                });
            }
            else {
                if (g_now) {
                    Object.defineProperty(this, g_now.get, {
                        get: function() {
                            return g_now.do(self);
                        }
                    });
                }
                if (s_now) {
                    Object.defineProperty(this, s_now.set, {
                        set: function(item) {
                            s_now.do(self, item);
                        }
                    });
                }
            }
        }
        if (extend) {
            base.prototype = extend.prototype;
            console.log(Object.keys(new base()));
        }
        var arr = [self];
        for(var k = 0; arguments[k] != undefined; k++) {
            arr.push(arguments[k]);
        }
        base.apply(this, arr);
    }
    return klass;
}
