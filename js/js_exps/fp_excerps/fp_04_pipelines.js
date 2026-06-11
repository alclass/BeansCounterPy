const DEFAULT_ODTPATH ="/home/dados/Books/odt Books"

function getDir(path) {
    const fs = require("fs");
    return fs.readdirSync(path);
}

const filterByText = (text, arr) => arr.filter(v => v.endsWith(text));
const filterOdt = arr => filterByText(".odt", arr);
const count = arr => arr.length;

/* pipeline by hand **/
const countOdtFiles = path => {
    const files = getDir(path);
    const filteredFiles = filterOdt(files);
    return count(filteredFiles);
};

const nOfOdtFiles = countOdtFiles(DEFAULT_ODTPATH); // 4, as with the command line solution
console.log("pipeline as with the command line solution");
console.log('Number of odt files in [', DEFAULT_ODTPATH, '] is', nOfOdtFiles);

const pipeTwo = (f, g) => (...args) => g(f(...args));

/* pipeline by 'fog' (my terming it) **/
const countOdtFiles3 = path =>
    pipeTwo(pipeTwo(getDir, filterOdt), count)(path)

console.log("pipeline by f(g(...))");
console.log('Number of odt files in [', DEFAULT_ODTPATH, '] is', countOdtFiles3(DEFAULT_ODTPATH));
