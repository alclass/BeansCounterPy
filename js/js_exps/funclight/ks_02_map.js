/*
Short/simple example with the 'unary pattern'
  Given a function as parameter, returns the same function accepting only one parameter
*/

// reuse unary_arrow() from another same-level-dir js-file
const { unary_arrow }  = require('./ks_01_unary.js')

function fMap(arr) {
  return arr.map(parseInt);
}

function fMap2(arr) {
  return arr.map(n => 2 * n)
}

function mapWithUnary(arr) {
  return arr.map(unary_arrow(parseInt))
}

let arr = ["1","2","3"]
let result = fMap(arr)
console.log('1 map with a direct ParseInt', arr, '.map(parseInt)', result);  // resp is 42
let arr2 = fMap2(arr)
console.log('2 map with arrow function', arr, '.map(x => 2 * n)', result);  // resp is 42
result = mapWithUnary(arr2)
console.log('2 map with mapWithUnary', arr2, '.map(unaray(parseInt))', result);  // resp is 42
