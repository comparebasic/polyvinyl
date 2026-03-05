
leftcol = document.getElementById("leftcol");
rightcol = document.getElementById("rightcol");

var s_left = "";
var s_right = "";

// colors = ["#ff4545", "#fff645", "#45ff48", "#45c7ff"]; // too bright
colors = ["#5c1717", "#5a5c17", "#175c18", "#17465c"];
dna = ["A", "C", "G", "T"];
rna = ["A", "C", "G", "U"];

/*
// trying to get this working: calculate the height and width of the table,
// divide by height and width of character to find exactly how many characters you can fit into the table

console.log(leftcol.getBoundingClientRect().width);
leftcol.innerHTML += `<span style="color:#5c1717">A</span>`;

const span = document.createElement("span");
span.style.height = "1ch";
span.style.width = "1ch";
span.style.position = "fixed";
document.body.appendChild(span);
const height = span.getBoundingClientRect().height;
const width = span.getBoundingClientRect().width;
document.body.removeChild(span);


console.log(leftcol.clientHeight / height);
console.log(leftcol.clientWidth / width);
console.log((leftcol.clientHeight / height) * (leftcol.clientWidth / width));

for (let i = 0; i < Math.floor(leftcol.clientWidth / Math.ceil(width)); i++) {
    r = Math.floor(Math.random() * 4);
    s_left = `<span style="color:${colors[r]}">${dna[r]}</span>`;
    leftcol.innerHTML += s_left;
} */

// too slow for big screens because it recalculates everything thousands of times
timeout = 0;

leftcol_height = leftcol.clientHeight;
while (leftcol.clientHeight == leftcol_height && timeout < 10000)
{
    r = Math.floor(Math.random() * 4);
    s_left = `<span style="color:${colors[r]}">${dna[r]}</span>`;
    leftcol.innerHTML += s_left;
    timeout += 1;
}
leftcol.innerHTML = leftcol.innerHTML.slice(0,-s_left.length);

rightcol_height = rightcol.clientHeight;
while (rightcol.clientHeight == rightcol_height && timeout < 10000)
{
    r = Math.floor(Math.random() * 4);
    s_right = `<span style="color:${colors[r]}">${rna[r]}</span>`;
    rightcol.innerHTML += s_right;
    timeout += 1;
}
rightcol.innerHTML = rightcol.innerHTML.slice(0,-s_right.length);
