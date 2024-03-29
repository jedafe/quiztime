'use strict';

// const readline = require('readline');

const questionaire = [
    {
        question: "A Thief is also known as___",
        category: "General",
        type: 'multiple',
        options: ['Criminal', 'Armed Robber', 'Doctor', 'Pirate'],
        answer: [0, 1, 3]
    },
    {
        question: 'Buhari is the current Nigeria President?',
        category: 'English',
        type: 'true-false',
        options: ['True', 'False'],
        answer: [0]
    },
    {
        question: 'Who owns Twitter?',
        category: 'English',
        type: 'single',
        options: ['Pius', 'Elon', 'Donald', 'Peter'],
        answer: [1]
    },
    {
        question: 'Who Controls Facebook?',
        category: 'Mathematics',
        type: 'single',
        options: ['Mark', 'Friday', 'Ben', 'Bryan'],
        answer: [0]
    },
    {
        question: "What is the name of Nigeria President?",
        category: 'Javascript',
        type: 'single',
        options: ["Olusegun Obasanjo", "Obafemi Awolowo", "Pius Anyim", "Muhammadu Buhari"],
        answer: [3]
    },
    {
        question: "Who is the Founder of Microsoft?",
        category: 'Javascript',
        type: 'single',
        options: ["Richard Bale", "Kingsley Duke", "Bill Gate", "Malik Jeffery"],
        answer: [2]
    },
    {
        question: "How many days do we have in a leap year?",
        category: 'Database',
        type: 'single',
        options: ["453 days", "355 days", "366 days", "365 days"],
        answer: [2]
    },
    {
        question: "How many weeks in a year?",
        category: 'General Knowledge',
        type: 'single',
        options: [52, 53, 54, 55],
        answer: [0]
    },
    {
        question: "What is the most popular Programming language in 2022?",
        category: 'Web Development',
        type: 'single',
        options: ["Java", "Javascript", "Python", "Golang"],
        answer: [1]
    }
]

// SAVE QUIZ TO LOCAL STORAGE
const quizForm = document.querySelector('form');

let quizTypeEl = document.querySelector('.quiz-type')

function switchQuizType() {
    let quizType = document.getElementById('quiz-type').value;
    switch (quizType) {
        case 'true-false':
            quizTypeEl.innerHTML = `
        <label
                          class="block h-full rounded-lg font-medium text-white mt-2">
                    <input type="text" value="False" class="input w-full option-a" name="options" hidden/>
                  </label>
                  <label
                          class="block h-full rounded-lg font-medium text-white mt-2">
                    <input type="text" value="True" class="input w-full option-b" name="options" hidden>
                  </label>
                  <label class="block h-full rounded-lg font-medium text-white mt-2 flex flex-wrap justify-between" >
                    <select class="input select w-3/6 answer" name="answer" required>
                      <option disabled selected>Chose Correct Answer</option>
                      <option value="0">False</option>
                      <option value="1">True</option>
                    </select>

                    <span class="text-center w-2/6 quiz-buttons">
                    <button type="submit" class="btn mr-2 bg-gray-800 w-full" id="submit">Submit</button>
                  </span>

                  </label>
    `;
            break;
        case 'single':
            quizTypeEl.innerHTML = `
        <label
                          class="block h-full rounded-lg font-medium text-white mt-2">
                    <input type="text" placeholder="Option A" class="input w-full option-a" name="options" required/>
                  </label>
                  <label
                          class="block h-full rounded-lg font-medium text-white mt-2">
                    <input type="text" placeholder="Option B" class="input w-full option-b" name="options" required>
                  </label>
                  <label class="block h-full rounded-lg font-medium text-white mt-2">
                    <input type="text" placeholder="Option C" class="input w-full option-c" name="options" required>
                  </label>
                  <label
                          class="block h-full rounded-lg font-medium text-white mt-2" >
                    <input type="text" placeholder="Option D" class="input w-full option-d" name="options" required>
                  </label>
                  <label class="block h-full rounded-lg font-medium text-white mt-2 flex flex-wrap justify-between" >
                    <select class="input select w-3/6 answer" name="answer" required>
                      <option disabled selected>Chose Correct Answer</option>
                      <option value="0">Option A</option>
                      <option value="1">Option B</option>
                      <option value="2">Option C</option>
                      <option value="3">Option D</option>
                    </select>

                    <span class="text-center w-2/6 quiz-buttons">
                    <button type="submit" class="btn mr-2 bg-gray-800 w-full" id="submit">Submit</button>
                  </span>

                  </label>
    `;
            break;
        case 'multiple':
            quizTypeEl.innerHTML = `
        <label
                          class="block h-full rounded-lg font-medium text-white mt-2">
                    <input type="text" placeholder="Option A" class="input w-full option-a" name="options" required/>
                  </label>
                  <label
                          class="block h-full rounded-lg font-medium text-white mt-2">
                    <input type="text" placeholder="Option B" class="input w-full option-b" name="options" required>
                  </label>
                  <label
                          class="block h-full rounded-lg font-medium text-white mt-2">
                    <input type="text" placeholder="Option C" class="input w-full option-c" name="options" required>
                  </label>
                  <label
                          class="block h-full rounded-lg font-medium text-white mt-2">
                    <input type="text" placeholder="Option D" class="input w-full option-d" name="options" required>
                  </label>
                  <div class="mt-2 mb-2 text-center"><span  class="block w-full text-lg">Select Correct Answers</span>
                  <label class="text-white mr-2">
                      <span>A</span> <input type="checkbox" name="answer" class="checkbox-sm" value="0">
                   </label>
                   <label class="text-white mr-2">
                      <span>B</span> <input type="checkbox" name="answer" class="checkbox-sm" value="1">
                    </label>
                    <label class="text-white mr-2">
                      <span>C</span> <input type="checkbox" name="answer" class="checkbox-sm" value="2">
                      </label>
                      <label class="text-white"  >
                      <span>D</span> <input type="checkbox" name="answer" class="checkbox-sm" value="3">
                      </label>
                     </div>

                    <span class="text-center w-2/6 quiz-buttons">
                     <button type="submit" class="btn mr-2 bg-gray-800 w-full" id="submit">Submit</button>
                    </span>


    `;
            break;
        default:
            alert("Select a value")
    }
}

quizForm.addEventListener('submit', (El) => {
    El.preventDefault();

    const formData = new FormData(El.target); // Converts Form Data to array of arrays
    // const formData = new FormData(form); // Converts Form Data to array of arrays

    const obj = Object.fromEntries(formData.entries()); // Array of arrays to object
    // const obj = Object.fromEntries(formData.entries()); // Array of arrays to object

    // for multi-selects, we need special handling
    obj.options = formData.getAll('options'); // All inputs options
    obj.answer = formData.getAll('answer'); // All Checkbox checked

    questionaire.push(obj);

    quizForm.reset() //clear the inputs

    //saving to localStorage
    localStorage.setItem("questionBank", JSON.stringify(questionaire))
});

// Retrieve All Quiz Object from local storage
let quizDB = localStorage.getItem("questionBank");
let quizOBJ = JSON.parse(quizDB)

// RANDOMIZE the Quiz Object (quizOBJ) to generate a Unique Randomize Question everytime.
const randomQuestionaire = [];
while(randomQuestionaire.length < quizOBJ.length) {
    let r = Math.floor(Math.random() * quizOBJ.length);
    if(randomQuestionaire.indexOf(quizOBJ[r]) === -1) randomQuestionaire.push(quizOBJ[r]);
}


const questions = document.getElementById('question')
const categoryEl = document.getElementById('category')
const optionBody = document.querySelector('.option-body')
const progress = document.querySelector('.progress')
const countDownTimer = document.querySelector('.count-down-timers')
const countUpTimer = document.querySelector('.count-up-timers')
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
let startQuizButton = document.querySelector('.start-quiz-button')
let createButton = document.querySelector('.create-quiz')
let createNewButton = document.querySelector('.create-new-quiz')

let timeLapse = 30 * randomQuestionaire.length;
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
    disableOption()
    disableButton()
    infoButton.style.display = 'none'
    infoBox.style.display = 'none'
    fullTimeLapse()

    document.querySelector('#create-new-quiz').style.display = 'none'
}
startQuiz()

startButton.addEventListener('click', () => {
    document.querySelector('#new-quiz').style.display = 'block'
    document.querySelector('#create-new-quiz').style.display = 'none'
    createNewButton.style.display = 'block'
    loadInfo()
    loadQuestion()
    countDown()
    countUp()
})
startQuizButton.addEventListener('click', () => {
    if (timeLapse < 0) {
        location.reload()
    } else {
        document.querySelector('#create-new-quiz').style.display = 'none'
        document.querySelector('#new-quiz').style.display = 'block'
        startQuizButton.style.display = 'none'
        createNewButton.style.display = 'block'
    }
})

createButton.addEventListener('click', () => {
    document.querySelector('#create-new-quiz').style.display = 'block'
    document.querySelector('#new-quiz').style.display = 'none'
})

createNewButton.addEventListener('click', () => {
    document.querySelector('#new-quiz').style.display = 'none'
    startQuizButton.style.display = 'block'
    createNewButton.style.display = 'none'
    document.querySelector('#create-new-quiz').style.display = 'block'
    document.querySelector('.start-new-quiz').style.display = 'block'
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

function loadOptions() {
    let newQuestion = randomQuestionaire[questionPage];
    categoryEl.textContent = newQuestion.category
    questions.textContent = newQuestion.question;
    let allOptions = ``;

    for (let i = 0; i < newQuestion.options.length; i++){
        if (newQuestion.answer.length > 1) {
            allOptions +=`
        <label class="block h-full rounded-lg border border-gray-700 p-4 hover:border-gray-500 font-medium text-white option-label" id="label-${i}">
            <input type="checkbox" class="checkbox option" id="${i}" name="quiz" />
            <span> ${newQuestion.options[i]}</span>
        </label>`
        } else {
            allOptions +=`
        <label class="block h-full rounded-lg border border-gray-700 p-4 hover:border-gray-500 font-medium text-white option-label" id="label-${i}">
            <input type="radio" class="radio option" id="${i}" name="quiz" />
            <span> ${newQuestion.options[i]}</span>
        </label>`
        }

    }
    return allOptions
}

function loadQuestion() {
    enableButton()
    optionBody.innerHTML = loadOptions()

    infoButton.textContent = ''
    startButton.style.display = 'none'
    infoButton.style.display = 'block'
    document.querySelector('.info-button').style.backgroundColor = "transparent";
}

    const countDown = function () {

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

    const countUp = function () {

        let count = 0
        let counter = setInterval(function () {
            const minute = Math.floor((count / 60)) % 60
            const seconds = Math.floor(count) % 60
            countUpMin.innerHTML = formatTime(minute);
            countUpSec.innerHTML = formatTime(seconds);
            count++;
            usedTimeCounter++

            if (count === timeLapse) {
                loadResult();
                clearInterval(counter)
                countUpTimer.innerHTML = `Time Up!!!`
            }
        }, 1000);
    }

    function finishedTime() {
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


    // function checkedOption() {
    //     const options = document.querySelectorAll('.option')
    //     let answer = undefined;
    //     options.forEach((option) => {
    //         if (option.checked) {
    //             answer = option.id
    //         }
    //
    //     })
    //     return answer
    // }

    function checkedOption() {
        const options = document.querySelectorAll('.option')
        let answer = [];
        options.forEach((option) => {
            if (option.checked) {
                answer.push(option.id)
            }

        })
        return answer
    }

    function checkedIsCorrectOption() {
        const options = document.querySelectorAll('.option')
        const optionLabels = document.querySelectorAll('.option-label')
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
        const options = document.querySelectorAll('.option')
        const optionLabels = document.querySelectorAll('.option-label')
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

// function toggleOption() {
//     options.forEach((option) => {
//         option.toggleAttribute('disabled')
//     })
// }

    function disableOption() {
        const options = document.querySelectorAll('.option')
        options.forEach((option) => {
            option.disabled = true
        })
    }

    function enableOption() {
        const options = document.querySelectorAll('.option')
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
        const options = document.querySelectorAll('.option')
        const optionLabels = document.querySelectorAll('.option-label')
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

        if (myAnswer.length > 0) {
            attemptedQuestion++
            if (myAnswer.toString() === randomQuestionaire[questionPage].answer.toString()) {
                correctAnswer++
                myPoints += 3
                averageScore = (myPoints / randomQuestionaire.length).toFixed(2);
            } else {
                wrongAnswer++
            }
            questionNumber++
            questionPage++

            if (questionPage < randomQuestionaire.length) {
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
        if (questionPage < randomQuestionaire.length) {
            clearSelected()
            loadQuestion()
            loadInfo()
            if (attemptedQuestion > 0) {
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

    checkAnswer.addEventListener('click', () => {
        document.querySelector('.error-info').textContent = ""
        countDownTimer.style.display = "none"
        let myAnswer = checkedOption();

        if (myAnswer.length > 0) {
            disableOption()
            document.querySelector('#skip').disabled = true;
            if (myAnswer.toString() === randomQuestionaire[questionPage].answer.toString()) {
                checkedIsCorrectOption()
            } else {
                checkedIsWrongOption()
            }
        } else {
            document.querySelector('.error-info').textContent = "Select an option first"
        }
    })

    function loadResult() {
    categoryEl.textContent = '';
        let percentageScore = correctAnswer / randomQuestionaire.length * 100;
        progress.style.display = 'none';
        optionBody.innerHTML = `<div class="text-center">

                <div class="stat place-items-center">
                  <div class="stat-title score">Score</div>
                  <div class="stat-value text-secondary score-value">${Math.round(percentageScore)}%</div>
                </div>

                <div class="radial-progress bg-secondary text-primary-content border-4 border-primary ml-3 mr-5" style="--value:${percentageScore};">${Math.round(percentageScore)}</div>


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



// console.log(questionaire[0].answer[0])