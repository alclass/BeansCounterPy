/* fp_01_make3curried2.js */

const make3 = (a, b, c) => String(100 * a + 10 * b + c);

const make3curried2 = function(a) {
    return function(b) {
        return function(c) {
            return String(100 * a + 10 * b + c);
        };
    };
};

console.log('make3', make3(1,2,3));
console.log('make3curried2', make3curried2(1)(2)(3));
