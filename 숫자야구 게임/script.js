const btn = document.querySelector(".submit-button");

let cnt = 9;
const cntSpan = document.getElementById("attempts");
cntSpan.textContent = cnt;


let num1 = Math.floor(Math.random() * 10);
    let num2 = Math.floor(Math.random() * 10);
    while (num2 == num1) {
    num2 = Math.floor(Math.random() * 10);
    }
    let num3 = Math.floor(Math.random() * 10);
    while (num3 == num1 || num3 == num2) {
    num3 = Math.floor(Math.random() * 10);
    }

console.log(num1,num2,num3)

btn.addEventListener("click", function () {

    let value =0;
    let position =0;

    const input11 = document.getElementById("number1");
    const input22 = document.getElementById("number2");
    const input33 = document.getElementById("number3");
    if (!input11.value || !input22.value || !input33.value) {
        input11.value = "";
        input22.value = "";
        input33.value = "";
        return;
    }
    
    const cntSpan = document.getElementById("attempts");


    const input1 = Number(document.getElementById("number1").value);
    const input2 = Number(document.getElementById("number2").value);
    const input3 = Number(document.getElementById("number3").value);
    


    if(input1 == num1 || input1 == num2 || input1 == num3) {
        if(input1 == num1){
            position += 1
        }else{value+=1}
    }
    if(input2 == num1 || input2 == num2 || input2 == num3){
        if(input2 == num2){
            position += 1
        }else{value+=1}
    }
    if(input3 == num1 || input3 == num2 || input3 == num3){
        if(input3 == num3){
            position += 1
        }else{value+=1}
    }
    const resultBox = document.querySelector(".result-display");
    const inputValue = `${input1} ${input2} ${input3}`;

    if (position === 0 && value === 0) {
        resultBox.innerHTML += `
        <div class="result-row"><br>
            ${inputValue} : <span class="num-result out">S</span>
        </div>
        `;
    } else {
        resultBox.innerHTML += `
        <div class="result-row"><br>
            ${inputValue} : ${position} <span class="num-result strike">S</span> ${value} <span class="num-result ball">B</span>
        </div> </span> 
        `;}


    
    cnt-=1;
    cntSpan.textContent = cnt;

    const resultImg = document.querySelector("#game-result-img");
    if (cnt == 0){
        resultImg.src = "fail.png";
        btn.disabled = true;

    }
    if (position == 3){
        resultImg.src = "success.png";
        btn.disabled = true;
    }

})