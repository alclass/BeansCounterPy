/* fp_01_make3curried2.js */


const make3 = (a, b, c) => String(100 * a + 10 * b + c);

const curryByBind = fn =>
    fn.length === 0 ? fn() : p => curryByBind(fn.bind(null, p));

console.log('make3', make3(1,2,3));
console.log('curryByBind', curryByBind(make3)(1)(2)(3));
