'use strict';

// const readline = require('readline');

const questionaire = [
    {
        question: 'Who is Nigeria President?',
        a: 'True',
        b: 'False',
        ans: 'c'
    },
    {
        question: 'Who owns Twitter?',
        a: 'Pius',
        b: 'Elon',
        c: 'Donald',
        d: 'Peter',
        ans: 'b'
    },
    {
        question: 'Who Controls Facebook?',
        a: 'Mark',
        b: 'Friday',
        c: 'Ben',
        d: 'Bryan',
        ans: 'a'
    },
    {
        question: "What is the name of Nigeria President?",
        a: "Olusegun Obasanjo",
        b: "Obafemi Awolowo",
        c: "Pius Anyim",
        d: "Muhammadu Buhari",
        ans: "d"
    },
    {
        question: "Who is the Founder of Microsoft?",
        a: "Richard Bale",
        b: "Kingsley Duke",
        c: "Bill Gate",
        d: "Malik Jeffery",
        ans: "c"
    },
    {
        question: "How many days do we have in a leap year?",
        a: "453 days",
        b: "355 days",
        c: "366 days",
        d: "365 days",
        ans: "c"
    },
    {
        question: "How may weeks in a year?",
        a: 52,
        b: 53,
        c: 54,
        d: 55,
        ans: "a"
    },
    {
        question: "What is the most popular Programming language in 2022?",
        a: "Java",
        b: "Javascript",
        c: "Python",
        d: "Golang",
        ans: "b"
    }
]

var randomQuestionaire = [];
while(randomQuestionaire.length < questionaire.length){
    var r = Math.floor(Math.random() * questionaire.length);
    if(randomQuestionaire.indexOf(questionaire[r]) === -1) randomQuestionaire.push(questionaire[r]);
}


const questions = document.getElementById('question')
const a = document.querySelector('#option-a')
const b = document.querySelector('#option-b')
const c = document.querySelector('#option-c')
const d = document.querySelector('#option-d')
const options = document.querySelectorAll('.option')
const optionBody = document.querySelector('.option-body')
const optionLabels = document.querySelectorAll('.option-label')
const progress = document.querySelector('.progress')
const  countDownTimer = document.querySelector('.count-down-timers')
const  countUpTimer = document.querySelector('.count-up-timers')
const countDownMin = document.querySelector('#count-down-min')
const countDownSec = document.querySelector('#count-down-sec')
const countUpMin = document.querySelector('#count-up-min')
const countUpSec = document.querySelector('#count-up-sec')


const checkAnswer = document.querySelector('#check')
const nextButton = document.querySelector('#next')
const skipButton = document.querySelector('#skip')
const buttons = document.querySelectorAll('.quiz-button')

let startBox = document.querySelector('.start-box')
let infoBox = document.querySelector('.info-box')
let infoButton = document.querySelector('.info-button')
let startButton = document.querySelector('.start-button')

let timeLapse = 4 * randomQuestionaire.length;
let usedTimeCounter = 0
const totalQuestion = randomQuestionaire.length
let attemptedQuestion = 0;
let skippedQuestion = 0;
let correctAnswer = 0;
let wrongAnswer = 0;
let questionNumber = 1;
let questionPage = 0;
let myPoints = 0;
let averageScore = 0;

function startQuiz() {
    // toggleOption()
    disableOption()
    disableButton()
    infoButton.style.display = 'none'
    infoBox.style.display = 'none'
    fullTimeLapse()
}
startQuiz()

startButton.addEventListener('click', () => {
    loadInfo()
    loadQuestion()
    countDown()
    countUp()
})

function loadInfo() {
    infoBox.style.display = 'block'
    startBox.style.display = 'none'
    progress.value =  questionNumber
    progress.max =  totalQuestion
    document.querySelector('.question-number').textContent = questionNumber
    document.querySelector('.total-question').textContent = totalQuestion
    document.querySelector('.attempted').textContent = attemptedQuestion
    document.querySelector('.correct').textContent = correctAnswer
    document.querySelector('.wrong').textContent = wrongAnswer
    document.querySelector('.skipped').textContent = skippedQuestion
    document.querySelector('.points').textContent = myPoints;
    document.querySelector('.average-score').textContent = averageScore;
    enableOption()
}

function loadQuestion() {
    enableButton()

    let newQuestion = randomQuestionaire[questionPage];
    questions.textContent = newQuestion.question;
    a.textContent = `A. ${newQuestion.a}`;
    b.textContent = `B. ${newQuestion.b}`;
    c.textContent = `C. ${newQuestion.c}`;
    d.textContent = `D. ${newQuestion.d}`;

    infoButton.textContent = ''
    startButton.style.display = 'none'
    infoButton.style.display = 'block'
    document.querySelector('.info-button').style.backgroundColor = "transparent";
}

const countDown = function() {

    let count = timeLapse
    let counter = setInterval(function () {
        const minute = Math.floor((count / 60)) % 60
        const seconds = Math.floor(count) % 60
        countDownMin.innerHTML = formatTime(minute);
        countDownSec.innerHTML = formatTime(seconds);
        count--;

        if (count === -1) {
            loadResult();
            clearInterval(counter)
            questions.innerHTML = `Time  Elapsed!!!`
        }
    }, 1000);
}

const countUp = function() {

    let count = 0
    let counter = setInterval(function () {
        const minute = Math.floor((count / 60)) % 60
        const seconds = Math.floor(count) % 60
        countUpMin.innerHTML = formatTime(minute);
        countUpSec.innerHTML = formatTime(seconds);
        // console.log(time);
        count++;
        usedTimeCounter++

        if (count === timeLapse) {
            loadResult();
            clearInterval(counter)
            countUpTimer.innerHTML = `Time Up!!!`
        }
    }, 1000);
}

function finishedTime(){
    const usedTime = usedTimeCounter
    const minute = Math.floor((usedTime / 60)) % 60
    const seconds = Math.floor(usedTime) % 60

    return `<h2 class="card-title text-right justify-center" ><div class="badge badge-secondary"> ${formatTime(minute)} : ${formatTime(seconds)} </div> </h2>`

}

function fullTimeLapse() {
    const quizTime = timeLapse
    const minute = Math.floor((quizTime / 60)) % 60
    const seconds = Math.floor(quizTime) % 60
    countDownMin.innerHTML = formatTime(minute);
    countDownSec.innerHTML = formatTime(seconds);

}

function formatTime(time) {
    return (time < 10) ? `0${time}` : time;
}


function checkedOption() {
    let answer = undefined;
    options.forEach((option) => {
        if(option.checked) {
            answer = option.id
        }
    })
    return answer
}

function checkedIsCorrectOption() {
    infoButton.textContent = 'Correct!'
    document.querySelector('.info-button').style.color = "green"

    options.forEach((option) => {
        if (option.checked) option.style.backgroundColor = "green"
    })

    optionLabels.forEach((optionLabel) => {
        if (optionLabel.id === "label-" + checkedOption())
            optionLabel.style.borderColor = "green"
    })
}

function checkedIsWrongOption() {
    infoButton.textContent = 'Wrong!'
    document.querySelector('.info-button').style.color = "#d926a9";

    options.forEach((option) => {
        if (option.checked) option.style.backgroundColor = "#d926a9"
    })

    optionLabels.forEach((optionLabel) => {
        if (optionLabel.id === "label-" + checkedOption())
            optionLabel.style.borderColor = "#d926a9"
    })
}
function disableOption() {
    options.forEach((option) => {
        option.disabled = true
    })
}

function enableOption() {
    options.forEach((option) => {
        option.disabled = false
    })
}

function disableButton() {
    buttons.forEach((button) => {
        button.disabled = true
    })
}
function enableButton() {
    buttons.forEach((button) => {
        button.disabled = false
    })
}

function clearSelected() {
    options.forEach((option) => {
        option.checked = false;
        option.style.backgroundColor = ""
    })
    optionLabels.forEach((optionLabel) => {
        optionLabel.style.borderColor = ""
    })
}

nextButton.addEventListener('click', () => {
    document.querySelector('.error-info').textContent = ""
    countDownTimer.style.display = "block"
    enableOption()
    document.querySelector('#skip').disabled = false;
    let myAnswer = checkedOption()

    if (myAnswer) {
        attemptedQuestion++
        if (myAnswer === randomQuestionaire[questionPage].ans){
            correctAnswer++
            myPoints += 3
            averageScore = myPoints / questionaire.length;
        } else {
            wrongAnswer++
        }
        questionNumber++
        questionPage++

        if (questionPage < questionaire.length){
            loadInfo()
            loadQuestion()
            clearSelected()

            document.querySelector('#restart').disabled = true;
        } else {
            loadInfo()
            loadResult()
            countDownTimer.innerHTML = `Time Spent ${finishedTime()}`;
            infoButton.style.display = 'none'
            countUpTimer.style.display = 'none'
        }
    } else {
        document.querySelector('.error-info').textContent = "Select an option to continue"
    }
})

skipButton.addEventListener('click', () => {
    document.querySelector('.error-info').textContent = ""

    questionNumber++
    questionPage++
    skippedQuestion++
    if (questionPage < questionaire.length){
        clearSelected()
        loadQuestion()
        loadInfo()
        if(attemptedQuestion > 0) {
            document.querySelector('#restart').disabled = true;
        }
    } else {
        loadInfo()
        loadResult()
        countDownTimer.innerHTML = `Time Spent ${finishedTime()}`;
        infoButton.style.display = 'none'
        countUpTimer.style.display = 'none'
    }

})

checkAnswer.addEventListener('click',  () => {
    document.querySelector('.error-info').textContent = ""
    countDownTimer.style.display = "none"
    let myAnswer = checkedOption()
    if (myAnswer) {
        disableOption()
        document.querySelector('#skip').disabled = true;
        if (myAnswer === randomQuestionaire[questionPage].ans){
            checkedIsCorrectOption()
        } else {
            checkedIsWrongOption()
        }
    } else {
        document.querySelector('.error-info').textContent = "Select an option first"
    }
})

function loadResult(){
    let percentageScore = correctAnswer / questionaire.length * 100;
    progress.style.display = 'none';
    optionBody.innerHTML = `<div class="text-center">

                <div class="stat place-items-center">
                  <div class="stat-title score">Score</div>
                  <div class="stat-value text-secondary score-value">${percentageScore}%</div>
                </div>
                
                <div class="radial-progress bg-secondary text-primary-content border-4 border-primary ml-3 mr-5" style="--value:${percentageScore};">${percentageScore}</div>


                <div class="stat place-items-right">
                  <div class="stat-title text-2xl grade">Grade</div>
                  <div class="stat-value text-3xl text-secondary grade-value">${percentageScore <= 40 ? 'Failed!' : percentageScore <= 59 ? 'Pass!' : percentageScore <= 69 ? 'Good!' : 'Excellent!'}</div>
                </div>
                </div>
<p class="text-center">You got <span class="text-secondary">${correctAnswer}</span> out of <span class="text-secondary">${totalQuestion}</span> questions</p>`
    disableButton();
    document.querySelector('#restart').disabled = false;
    questions.textContent = 'The End!'
    document.querySelector('.question-info').innerHTML = `${percentageScore < 60 ? 'Try Again!!!' : 'Congratulations!!!'}`
}



// function quest(opt) {
//     for (let i = 0; i < opt.length; i++) {
    //     let ans = prompt(`
    //     ${opt[i].q}:
    //     A: ${opt[i]['A']}
    //     B: ${opt[i]['B']}
    //     C: ${opt[i]['C']}
    //     D: ${opt[i]['D']}
    //   `);
    //
    //     if (ans.toUpperCase() === opt[i].Ans) {
    //         alert('Right Answer')
    //     } else {
    //         alert('Wrong Answer')
    //     }
    // }
// }
//
// quest(ques)

// const rl = readline.createInterface({
//     input: process.stdin,
//     output: process.stdout,
// });

// Iterate through the object
// for (const key in population) {
//     console.log(`${key}`);
// }



// label.addEventListener('click', () => {
//         label.style.backgroundColor = "green";
// })

// $('#radio-label').click(function() {
//     if($('#input-radio').is(':checked')) {
//         $('#radio-label').toggleClass('has-background-color'); }
// });