/*
js_exps/funclight/ks_01_unary.js
Short/simple example with the 'unary pattern'
  Given a function as parameter, returns the same function accepting only one parameter
*/

function unary(fn) {
  return function onlyOneArg(arg){
    return fn( arg );
  };
}

let unary_arrow =
  fn =>
    arg =>
      fn( arg );


function fSum3p(a, b, c) {
  /* because it may be transformed to 'unary', 'protect' following parameters  */
  if (b == undefined) b = 0;
  if (c == undefined) c = 0;
  return a + b + c;
}

let fSum3pUnaried = unary_arrow(fSum3p);
resp = fSum3pUnaried(42)
console.log('1 resp', resp);  // resp is 42
resp = fSum3pUnaried(42, 10, 10);  // linter complains when passing more than one parameter to 'unary'
console.log('2 resp', resp);  // resp is 42 (the parameters after the first are 'lost')
resp = fSum3p(2, 10, 30)
console.log('3 fArgs', resp);  // the three arguments are summed up 2+10+30=42

module.exports = { unary_arrow };